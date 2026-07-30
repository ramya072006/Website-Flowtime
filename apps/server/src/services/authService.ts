import crypto from 'crypto';
import bcrypt from 'bcryptjs';
import { User } from '../models/User';
import { Calendar } from '../models/Calendar';
import { generateTokenPair, verifyRefreshToken } from '../utils/jwt';
import { AppError } from '../middlewares/errorHandler';
import { emailService } from './emailService';

// ── Helpers ───────────────────────────────────────────────────────────────────
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;

function validatePassword(password: string) {
  if (!PASSWORD_REGEX.test(password)) {
    throw new AppError(
      'Password must be at least 8 characters and include uppercase, lowercase, number, and special character',
      400
    );
  }
}

function generateOtp(): string {
  // Cryptographically secure 6-digit OTP
  return String(crypto.randomInt(100000, 999999));
}

// ── Service ───────────────────────────────────────────────────────────────────
export const authService = {
  // ── REGISTER ────────────────────────────────────────────────────────────────
  async register(name: string, email: string, password: string, confirmPassword?: string, timezone = 'UTC') {
    if (!name?.trim()) throw new AppError('Name is required', 400);
    if (!email?.trim()) throw new AppError('Email is required', 400);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new AppError('Invalid email format', 400);
    if (!password) throw new AppError('Password is required', 400);
    if (confirmPassword !== undefined && password !== confirmPassword) {
      throw new AppError('Passwords do not match', 400);
    }
    validatePassword(password);

    const existing = await User.findOne({ email: email.toLowerCase() });
    if (existing) throw new AppError('Email already registered', 409);

    const otp = generateOtp();
    const otpHash = await bcrypt.hash(otp, 10);
    const otpExpires = new Date(Date.now() + 10 * 60 * 1000); // 10 min

    const user = await User.create({
      name: name.trim(),
      email: email.toLowerCase(),
      password,
      timezone,
      status: 'pending',
      isEmailVerified: false,
      otpCode: otpHash,
      otpExpires,
    });

    // Default calendar
    await Calendar.create({
      name: 'My Calendar',
      color: '#6366f1',
      provider: 'flowtime',
      isDefault: true,
      isPrimary: true,
      userId: user._id,
    });

    // Send OTP email — fully non-blocking, never delay registration response
    setImmediate(() => {
      emailService.sendOtpEmail(user.email, user.name, otp).catch(() => {});
    });

    return { userId: user._id.toString(), email: user.email };
  },

  // ── VERIFY OTP ───────────────────────────────────────────────────────────────
  async verifyOtp(email: string, otp: string) {
    const user = await User.findOne({ email: email.toLowerCase() })
      .select('+otpCode +otpExpires');
    if (!user) throw new AppError('User not found', 404);
    if (user.isEmailVerified) throw new AppError('Email already verified', 400);
    if (!user.otpCode || !user.otpExpires) throw new AppError('No pending OTP. Please request a new one.', 400);
    if (user.otpExpires < new Date()) throw new AppError('OTP has expired. Please request a new one.', 400);

    const isValid = await bcrypt.compare(otp, user.otpCode);
    if (!isValid) throw new AppError('Invalid OTP code', 400);

    // Mark verified, activate account, clear OTP
    user.isEmailVerified = true;
    user.status = 'active';
    user.otpCode = undefined;
    user.otpExpires = undefined;
    await user.save();

    // Issue tokens
    const tokens = generateTokenPair({
      userId: user._id.toString(),
      email: user.email,
      role: user.role,
    });

    await User.findByIdAndUpdate(user._id, {
      $push: { refreshTokens: tokens.refreshToken },
      lastLogin: new Date(),
    });

    return { user, tokens };
  },

  // ── RESEND OTP ───────────────────────────────────────────────────────────────
  async resendOtp(email: string) {
    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return; // don't reveal if email exists
    if (user.isEmailVerified) throw new AppError('Email already verified', 400);

    const otp = generateOtp();
    const otpHash = await bcrypt.hash(otp, 10);
    const otpExpires = new Date(Date.now() + 10 * 60 * 1000);

    await User.findByIdAndUpdate(user._id, { otpCode: otpHash, otpExpires });
    // Non-blocking
    setImmediate(() => {
      emailService.sendOtpEmail(user.email, user.name, otp).catch(() => {});
    });
  },

  // ── LOGIN ────────────────────────────────────────────────────────────────────
  async login(email: string, password: string) {
    if (!email || !password) throw new AppError('Email and password are required', 400);

    const user = await User.findOne({ email: email.toLowerCase() })
      .select('+password +refreshTokens +loginAttempts +lockUntil');

    if (!user || !user.password) throw new AppError('Invalid email or password', 401);

    // Account locked?
    if (user.isLocked()) {
      const minutesLeft = Math.ceil((user.lockUntil!.getTime() - Date.now()) / 60000);
      throw new AppError(`Account locked. Try again in ${minutesLeft} minute${minutesLeft !== 1 ? 's' : ''}.`, 423);
    }

    const isValid = await user.comparePassword(password);
    if (!isValid) {
      await user.incLoginAttempts();
      // Reload to get updated attempts count
      const updated = await User.findById(user._id).select('+loginAttempts');
      const remaining = Math.max(0, 5 - (updated?.loginAttempts ?? 0));
      if (remaining === 0) {
        throw new AppError('Account locked for 15 minutes due to too many failed attempts.', 423);
      }
      throw new AppError(
        `Invalid email or password. ${remaining} attempt${remaining !== 1 ? 's' : ''} remaining.`,
        401
      );
    }

    // Email verified?
    if (!user.isEmailVerified) {
      throw new AppError('Please verify your email before logging in.', 403);
    }

    // Account active?
    if (user.status === 'inactive') {
      throw new AppError('Your account has been deactivated. Contact support.', 403);
    }

    await user.resetLoginAttempts();

    const tokens = generateTokenPair({
      userId: user._id.toString(),
      email: user.email,
      role: user.role,
    });

    // Keep last 5 refresh tokens (multi-device)
    const refreshTokens = [...(user.refreshTokens || []), tokens.refreshToken].slice(-5);
    await User.findByIdAndUpdate(user._id, {
      refreshTokens,
      lastLogin: new Date(),
      lastActive: new Date(),
    });

    return { user, tokens };
  },

  // ── LOGOUT ───────────────────────────────────────────────────────────────────
  async logout(userId: string, refreshToken: string) {
    await User.findByIdAndUpdate(userId, {
      $pull: { refreshTokens: refreshToken },
    });
  },

  // ── REFRESH TOKENS ───────────────────────────────────────────────────────────
  async refreshTokens(refreshToken: string) {
    const payload = verifyRefreshToken(refreshToken);
    const user = await User.findById(payload.userId).select('+refreshTokens');
    if (!user) throw new AppError('User not found', 401);

    if (!user.refreshTokens?.includes(refreshToken)) {
      // Token reuse detected — invalidate all tokens
      await User.findByIdAndUpdate(user._id, { refreshTokens: [] });
      throw new AppError('Token reuse detected. Please log in again.', 401);
    }

    const tokens = generateTokenPair({
      userId: user._id.toString(),
      email: user.email,
      role: user.role,
    });

    const newTokens = user.refreshTokens
      .filter((t) => t !== refreshToken)
      .concat(tokens.refreshToken)
      .slice(-5);

    await User.findByIdAndUpdate(user._id, { refreshTokens: newTokens });
    return tokens;
  },

  // ── FORGOT PASSWORD ──────────────────────────────────────────────────────────
  async forgotPassword(email: string) {
    if (!email) throw new AppError('Email is required', 400);

    const user = await User.findOne({ email: email.toLowerCase() });
    if (!user) return; // don't reveal if email exists

    const rawToken = crypto.randomBytes(32).toString('hex');
    const hashedToken = crypto.createHash('sha256').update(rawToken).digest('hex');

    await User.findByIdAndUpdate(user._id, {
      passwordResetToken: hashedToken,
      passwordResetExpires: new Date(Date.now() + 60 * 60 * 1000), // 1 hour
    });

    // Fully non-blocking — never await email, never throw from it
    setImmediate(() => {
      emailService.sendPasswordResetEmail(user.email, user.name, rawToken).catch(() => {});
    });
  },

  // ── RESET PASSWORD ───────────────────────────────────────────────────────────
  async resetPassword(email: string, token: string, newPassword: string, confirmPassword?: string) {
    if (!email || !token || !newPassword) throw new AppError('Email, token and new password are required', 400);
    if (confirmPassword !== undefined && newPassword !== confirmPassword) {
      throw new AppError('Passwords do not match', 400);
    }
    validatePassword(newPassword);

    const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
    const user = await User.findOne({
      email: email.toLowerCase(),
      passwordResetToken: hashedToken,
      passwordResetExpires: { $gt: new Date() },
    }).select('+passwordResetToken +passwordResetExpires +refreshTokens');

    if (!user) throw new AppError('Invalid or expired reset link. Please request a new one.', 400);

    user.password = newPassword;
    user.passwordResetToken = undefined;
    user.passwordResetExpires = undefined;
    user.refreshTokens = []; // invalidate all sessions
    await user.save();

    // Send confirmation email (non-blocking)
    emailService.sendPasswordChangedEmail(user.email, user.name).catch(() => {});

    return user;
  },

  // ── GOOGLE OAUTH ─────────────────────────────────────────────────────────────
  async googleOAuth(profile: {
    id: string;
    emails?: Array<{ value: string }>;
    displayName: string;
    photos?: Array<{ value: string }>;
  }) {
    const email = profile.emails?.[0]?.value;
    if (!email) throw new AppError('No email from Google', 400);

    let user = await User.findOne({ $or: [{ googleId: profile.id }, { email }] });

    if (!user) {
      user = await User.create({
        name: profile.displayName,
        email,
        googleId: profile.id,
        avatar: profile.photos?.[0]?.value,
        isEmailVerified: true,
        status: 'active',
      });
      await Calendar.create({
        name: 'My Calendar',
        color: '#6366f1',
        provider: 'flowtime',
        isDefault: true,
        isPrimary: true,
        userId: user._id,
      });
    } else if (!user.googleId) {
      await User.findByIdAndUpdate(user._id, {
        googleId: profile.id,
        isEmailVerified: true,
        status: 'active',
      });
    }

    const tokens = generateTokenPair({
      userId: user._id.toString(),
      email: user.email,
      role: user.role,
    });

    await User.findByIdAndUpdate(user._id, {
      $push: { refreshTokens: tokens.refreshToken },
      lastLogin: new Date(),
      lastActive: new Date(),
    });

    return { user, tokens };
  },
};

import { Request, Response } from 'express';
import { authService } from '../services/authService';
import { sendSuccess, sendCreated, sendError } from '../utils/apiResponse';
import { asyncHandler } from '../utils/asyncHandler';
import { AuthRequest } from '../middlewares/auth';
import { User } from '../models/User';

export const authController = {
  // POST /api/auth/register
  register: asyncHandler(async (req: Request, res: Response) => {
    const { name, email, password, confirmPassword, timezone } = req.body;
    const result = await authService.register(name, email, password, confirmPassword, timezone);
    sendCreated(res, result, 'Registration successful. Please check your email for the verification code.');
  }),

  // POST /api/auth/verify-otp
  verifyOtp: asyncHandler(async (req: Request, res: Response) => {
    const { email, otp } = req.body;
    if (!email || !otp) { sendError(res, 'Email and OTP are required', 400); return; }
    const result = await authService.verifyOtp(email, otp.trim());
    sendSuccess(res, { user: result.user, tokens: result.tokens }, 'Email verified successfully');
  }),

  // POST /api/auth/resend-otp
  resendOtp: asyncHandler(async (req: Request, res: Response) => {
    const { email } = req.body;
    if (!email) { sendError(res, 'Email is required', 400); return; }
    await authService.resendOtp(email);
    sendSuccess(res, null, 'If that email is registered and unverified, a new code has been sent');
  }),

  // POST /api/auth/login
  login: asyncHandler(async (req: Request, res: Response) => {
    const { email, password } = req.body;
    const result = await authService.login(email, password);
    sendSuccess(res, { user: result.user, tokens: result.tokens }, 'Login successful');
  }),

  // POST /api/auth/logout
  logout: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { refreshToken } = req.body;
    if (req.user && refreshToken) {
      await authService.logout(req.user.userId, refreshToken);
    }
    sendSuccess(res, null, 'Logged out successfully');
  }),

  // POST /api/auth/refresh
  refreshToken: asyncHandler(async (req: Request, res: Response) => {
    const { refreshToken } = req.body;
    if (!refreshToken) { sendError(res, 'Refresh token required', 400); return; }
    const tokens = await authService.refreshTokens(refreshToken);
    sendSuccess(res, tokens, 'Tokens refreshed');
  }),

  // POST /api/auth/forgot-password
  forgotPassword: asyncHandler(async (req: Request, res: Response) => {
    const { email } = req.body;
    await authService.forgotPassword(email);
    // Always same message — never reveal if email exists
    sendSuccess(res, null, 'If that email exists, a reset link has been sent');
  }),

  // POST /api/auth/reset-password
  resetPassword: asyncHandler(async (req: Request, res: Response) => {
    const { email, token, password, confirmPassword } = req.body;
    await authService.resetPassword(email, token, password, confirmPassword);
    sendSuccess(res, null, 'Password reset successfully. You can now log in with your new password.');
  }),

  // GET /api/auth/me
  getMe: asyncHandler(async (req: AuthRequest, res: Response) => {
    const user = await User.findById(req.user?.userId);
    if (!user) { sendError(res, 'User not found', 404); return; }
    sendSuccess(res, user);
  }),

  // PATCH /api/auth/profile
  updateProfile: asyncHandler(async (req: AuthRequest, res: Response) => {
    const allowed = ['name', 'avatar', 'timezone', 'workHours', 'sleepHours',
      'productivityPreferences', 'focusPreferences', 'aiSettings', 'notificationSettings'];
    const updates: Record<string, unknown> = {};
    for (const field of allowed) {
      if (req.body[field] !== undefined) updates[field] = req.body[field];
    }
    const user = await User.findByIdAndUpdate(req.user?.userId, updates, { new: true, runValidators: true });
    if (!user) { sendError(res, 'User not found', 404); return; }
    sendSuccess(res, user, 'Profile updated');
  }),

  // PATCH /api/auth/change-password
  changePassword: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { currentPassword, newPassword, confirmPassword } = req.body;
    const user = await User.findById(req.user?.userId).select('+password');
    if (!user) { sendError(res, 'User not found', 404); return; }

    const isValid = await user.comparePassword(currentPassword);
    if (!isValid) { sendError(res, 'Current password is incorrect', 400); return; }

    if (newPassword !== confirmPassword) { sendError(res, 'Passwords do not match', 400); return; }

    user.password = newPassword;
    user.refreshTokens = [];
    await user.save();
    sendSuccess(res, null, 'Password changed successfully');
  }),
};

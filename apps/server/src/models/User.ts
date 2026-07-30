import mongoose, { Document, Schema } from 'mongoose';
import bcrypt from 'bcryptjs';

export interface IUser extends Document {
  name: string;
  email: string;
  password?: string;
  avatar?: string;
  timezone: string;
  status: 'pending' | 'active' | 'inactive';
  workHours: { start: string; end: string; days: number[] };
  sleepHours: { bedtime: string; wakeTime: string };
  productivityPreferences: {
    peakHours: string[];
    preferredFocusDuration: number;
    breakDuration: number;
    deepWorkBlocks: number;
  };
  focusPreferences: {
    protectMornings: boolean;
    protectAfternoons: boolean;
    minFocusBlock: number;
    maxMeetingsPerDay: number;
  };
  aiSettings: {
    autoSchedule: boolean;
    autoReschedule: boolean;
    learningEnabled: boolean;
    suggestionFrequency: string;
  };
  notificationSettings: {
    email: boolean;
    push: boolean;
    inApp: boolean;
    reminderMinutes: number[];
    deadlineAlerts: boolean;
    aiSuggestions: boolean;
  };
  connectedCalendars: Array<{
    provider: string;
    accountEmail: string;
    calendarId: string;
    syncEnabled: boolean;
    accessToken?: string;
    refreshToken?: string;
    lastSynced?: Date;
  }>;
  onboardingCompleted: boolean;
  role: 'user' | 'admin';
  // OTP-based email verification
  isEmailVerified: boolean;
  emailVerified: boolean; // alias kept for backward compat
  otpCode?: string;           // bcrypt hash of OTP, select: false
  otpExpires?: Date;          // select: false
  // Password reset
  passwordResetToken?: string;    // SHA-256 hash, select: false
  passwordResetExpires?: Date;    // select: false
  // Account locking
  loginAttempts: number;
  lockUntil?: Date;
  // Tokens
  refreshTokens: string[];        // select: false
  // OAuth
  googleId?: string;
  microsoftId?: string;
  lastLogin?: Date;
  lastActive?: Date;
  createdAt: Date;
  updatedAt: Date;
  comparePassword(candidatePassword: string): Promise<boolean>;
  isLocked(): boolean;
  incLoginAttempts(): Promise<void>;
  resetLoginAttempts(): Promise<void>;
}

const UserSchema = new Schema<IUser>(
  {
    name: { type: String, required: true, trim: true, maxlength: 100 },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true },
    password: { type: String, select: false },
    avatar: { type: String },
    timezone: { type: String, default: 'UTC' },
    status: { type: String, enum: ['pending', 'active', 'inactive'], default: 'pending' },
    workHours: {
      start: { type: String, default: '09:00' },
      end: { type: String, default: '17:00' },
      days: { type: [Number], default: [1, 2, 3, 4, 5] },
    },
    sleepHours: {
      bedtime: { type: String, default: '23:00' },
      wakeTime: { type: String, default: '07:00' },
    },
    productivityPreferences: {
      peakHours: { type: [String], default: ['09:00', '10:00', '11:00'] },
      preferredFocusDuration: { type: Number, default: 90 },
      breakDuration: { type: Number, default: 15 },
      deepWorkBlocks: { type: Number, default: 2 },
    },
    focusPreferences: {
      protectMornings: { type: Boolean, default: true },
      protectAfternoons: { type: Boolean, default: false },
      minFocusBlock: { type: Number, default: 30 },
      maxMeetingsPerDay: { type: Number, default: 4 },
    },
    aiSettings: {
      autoSchedule: { type: Boolean, default: true },
      autoReschedule: { type: Boolean, default: true },
      learningEnabled: { type: Boolean, default: true },
      suggestionFrequency: { type: String, default: 'medium' },
    },
    notificationSettings: {
      email: { type: Boolean, default: true },
      push: { type: Boolean, default: true },
      inApp: { type: Boolean, default: true },
      reminderMinutes: { type: [Number], default: [15, 60] },
      deadlineAlerts: { type: Boolean, default: true },
      aiSuggestions: { type: Boolean, default: true },
    },
    connectedCalendars: [
      {
        provider: String,
        accountEmail: String,
        calendarId: String,
        syncEnabled: { type: Boolean, default: true },
        accessToken: { type: String, select: false },
        refreshToken: { type: String, select: false },
        lastSynced: Date,
      },
    ],
    onboardingCompleted: { type: Boolean, default: false },
    role: { type: String, enum: ['user', 'admin'], default: 'user' },
    // Email verification via OTP
    isEmailVerified: { type: Boolean, default: false },
    otpCode: { type: String, select: false },
    otpExpires: { type: Date, select: false },
    // Password reset
    passwordResetToken: { type: String, select: false },
    passwordResetExpires: { type: Date, select: false },
    // Account locking
    loginAttempts: { type: Number, default: 0 },
    lockUntil: { type: Date },
    // Refresh tokens (array supports multiple devices)
    refreshTokens: { type: [String], select: false, default: [] },
    // OAuth
    googleId: { type: String, sparse: true },
    microsoftId: { type: String, sparse: true },
    lastLogin: { type: Date },
    lastActive: { type: Date },
  },
  { timestamps: true }
);

// ── Indexes ──────────────────────────────────────────────────────────────────
UserSchema.index({ email: 1 }, { unique: true });
UserSchema.index({ status: 1 });
UserSchema.index({ passwordResetExpires: 1 });
UserSchema.index({ googleId: 1 }, { sparse: true });
UserSchema.index({ microsoftId: 1 }, { sparse: true });

// ── Virtual: emailVerified alias ─────────────────────────────────────────────
UserSchema.virtual('emailVerified').get(function () {
  return this.isEmailVerified;
});

// ── Hash password before save ────────────────────────────────────────────────
UserSchema.pre('save', async function (next) {
  if (!this.isModified('password') || !this.password) return next();
  this.password = await bcrypt.hash(this.password, 10);
  next();
});

// ── Instance methods ─────────────────────────────────────────────────────────
UserSchema.methods.comparePassword = async function (candidate: string): Promise<boolean> {
  if (!this.password) return false;
  return bcrypt.compare(candidate, this.password);
};

UserSchema.methods.isLocked = function (): boolean {
  return !!(this.lockUntil && this.lockUntil > new Date());
};

UserSchema.methods.incLoginAttempts = async function (): Promise<void> {
  const MAX_ATTEMPTS = 5;
  const LOCK_TIME = 15 * 60 * 1000; // 15 minutes

  // If previous lock has expired, reset
  if (this.lockUntil && this.lockUntil < new Date()) {
    await this.model('User').findByIdAndUpdate(this._id, {
      loginAttempts: 1,
      $unset: { lockUntil: 1 },
    });
    return;
  }

  const update: Record<string, unknown> = { $inc: { loginAttempts: 1 } };
  if (this.loginAttempts + 1 >= MAX_ATTEMPTS) {
    update.lockUntil = new Date(Date.now() + LOCK_TIME);
  }
  await this.model('User').findByIdAndUpdate(this._id, update);
};

UserSchema.methods.resetLoginAttempts = async function (): Promise<void> {
  await this.model('User').findByIdAndUpdate(this._id, {
    loginAttempts: 0,
    $unset: { lockUntil: 1 },
  });
};

// ── Strip sensitive fields from JSON output ──────────────────────────────────
UserSchema.methods.toJSON = function () {
  const obj = this.toObject({ virtuals: true });
  delete obj.password;
  delete obj.refreshTokens;
  delete obj.otpCode;
  delete obj.otpExpires;
  delete obj.passwordResetToken;
  delete obj.passwordResetExpires;
  return obj;
};

export const User = mongoose.model<IUser>('User', UserSchema);

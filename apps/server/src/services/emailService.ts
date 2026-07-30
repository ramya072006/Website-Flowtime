import nodemailer from 'nodemailer';
import { config } from '../config';
import { logger } from '../utils/logger';

// ── Transporter ───────────────────────────────────────────────────────────────
const createTransporter = () => {
  if (!config.email.user || !config.email.pass) {
    logger.warn('Email not configured (SMTP_USER / SMTP_PASS missing)');
    return null;
  }
  return nodemailer.createTransport({
    host: config.email.host,   // smtp.gmail.com
    port: config.email.port,   // 587
    secure: false,             // STARTTLS
    auth: {
      user: config.email.user,
      pass: config.email.pass, // Gmail App Password (16 chars, no spaces)
    },
    tls: { rejectUnauthorized: false },
  });
};

const transporter = createTransporter();

// ── Shared HTML wrapper ───────────────────────────────────────────────────────
const html = (body: string) => `
  <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 560px; margin: 0 auto;
              background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden;">
    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 32px 40px;">
      <h1 style="color: white; margin: 0; font-size: 24px; font-weight: 700;">⚡ FlowTime</h1>
    </div>
    <div style="padding: 32px 40px;">${body}</div>
    <div style="padding: 16px 40px; background: #f9fafb; border-top: 1px solid #e5e7eb;">
      <p style="margin: 0; font-size: 12px; color: #9ca3af;">
        You received this email because you have a FlowTime account. If you didn't request this, ignore it.
      </p>
    </div>
  </div>
`;

const send = async (to: string, subject: string, htmlBody: string) => {
  if (!transporter) {
    logger.warn(`Email not sent to ${to} — transporter not configured`);
    return;
  }
  try {
    await transporter.sendMail({
      from: config.email.from,
      to,
      subject,
      html: htmlBody,
    });
    logger.info(`Email sent to ${to}: ${subject}`);
  } catch (err) {
    logger.error(`Failed to send email to ${to}:`, err);
    throw err; // let callers handle if they want
  }
};

// ── Public API ────────────────────────────────────────────────────────────────
export const emailService = {
  /** Send 6-digit OTP for email verification */
  async sendOtpEmail(email: string, name: string, otp: string) {
    await send(
      email,
      'Your FlowTime verification code',
      html(`
        <h2 style="color: #111827; margin-top: 0;">Verify your email</h2>
        <p style="color: #374151;">Hi <strong>${name}</strong>, use the code below to verify your email address.</p>
        <div style="background: #f3f4f6; border-radius: 8px; padding: 24px; text-align: center; margin: 24px 0;">
          <span style="font-size: 40px; font-weight: 800; letter-spacing: 12px; color: #6366f1;">${otp}</span>
        </div>
        <p style="color: #6b7280; font-size: 14px;">This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
      `)
    );
  },

  /** Send password reset link */
  async sendPasswordResetEmail(email: string, name: string, token: string) {
    const resetUrl = `${config.clientUrl}/reset-password?token=${token}&email=${encodeURIComponent(email)}`;
    await send(
      email,
      'Reset your password',
      html(`
        <h2 style="color: #111827; margin-top: 0;">Reset your password</h2>
        <p style="color: #374151;">Hi <strong>${name}</strong>, we received a request to reset your FlowTime password.</p>
        <div style="margin: 24px 0;">
          <a href="${resetUrl}"
             style="background: #6366f1; color: white; padding: 14px 28px; text-decoration: none;
                    border-radius: 8px; display: inline-block; font-weight: 600; font-size: 15px;">
            Reset Password
          </a>
        </div>
        <p style="color: #6b7280; font-size: 14px;">This link expires in <strong>1 hour</strong>. If you didn't request this, ignore this email — your password won't change.</p>
        <p style="color: #9ca3af; font-size: 12px; word-break: break-all;">Or copy this link: ${resetUrl}</p>
      `)
    );
  },

  /** Send password changed confirmation */
  async sendPasswordChangedEmail(email: string, name: string) {
    await send(
      email,
      'Your password has been changed',
      html(`
        <h2 style="color: #111827; margin-top: 0;">Password changed</h2>
        <p style="color: #374151;">Hi <strong>${name}</strong>, your FlowTime password was successfully changed.</p>
        <p style="color: #374151;">If you didn't make this change, please <a href="${config.clientUrl}/forgot-password" style="color: #6366f1;">reset your password immediately</a>.</p>
      `)
    );
  },

  /** Generic notification email */
  async sendNotificationEmail(email: string, subject: string, message: string) {
    await send(email, subject, html(`<p style="color: #374151;">${message}</p>`)).catch(() => {});
  },
};

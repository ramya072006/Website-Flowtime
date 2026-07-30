import nodemailer from 'nodemailer';
import { config } from '../config';
import { logger } from '../utils/logger';

// ── Lazy transporter using Brevo SMTP relay ───────────────────────────────────
// Brevo SMTP (smtp-relay.brevo.com:587) is NOT blocked by Render unlike Gmail
let _transporter: nodemailer.Transporter | null | undefined = undefined;

const getTransporter = (): nodemailer.Transporter | null => {
  if (_transporter !== undefined) return _transporter;

  const user = process.env.BREVO_SMTP_USER;   // your Brevo login email
  const pass = process.env.BREVO_SMTP_KEY;    // the xsmtpsib-... key

  if (!user || !pass) {
    logger.warn('BREVO_SMTP_USER or BREVO_SMTP_KEY not set — emails will not be sent');
    _transporter = null;
    return null;
  }

  logger.info(`Creating Brevo SMTP transporter for ${user}`);
  _transporter = nodemailer.createTransport({
    host: 'smtp-relay.brevo.com',
    port: 465,
    secure: true,
    auth: { user, pass },
    tls: { rejectUnauthorized: false },
    connectionTimeout: 15000,
    greetingTimeout: 15000,
    socketTimeout: 20000,
  });
  return _transporter;
};

const FROM_NAME  = 'TaskManagement';
const FROM_EMAIL = process.env.BREVO_FROM_EMAIL || 'ramyasribalivada@gmail.com';

// ── HTML wrapper ──────────────────────────────────────────────────────────────
const wrap = (body: string) => `
  <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:560px;margin:0 auto;
              background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:32px 40px;">
      <h1 style="color:white;margin:0;font-size:24px;font-weight:700;">✅ TaskManagement</h1>
    </div>
    <div style="padding:32px 40px;">${body}</div>
    <div style="padding:16px 40px;background:#f9fafb;border-top:1px solid #e5e7eb;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">
        You received this because you have a TaskManagement account.
        If you didn't request this, you can safely ignore it.
      </p>
    </div>
  </div>
`;

// ── Core send ─────────────────────────────────────────────────────────────────
const send = async (to: string, subject: string, html: string): Promise<void> => {
  const t = getTransporter();
  if (!t) {
    logger.warn(`Email skipped — no transporter. To: ${to}`);
    return;
  }
  logger.info(`Sending email to: ${to}`);
  const info = await t.sendMail({
    from: `"${FROM_NAME}" <${FROM_EMAIL}>`,
    to,
    subject,
    html,
  });
  logger.info(`Email sent — messageId: ${info.messageId}, to: ${to}`);
};

// ── Public methods ────────────────────────────────────────────────────────────
export const emailService = {
  async sendOtpEmail(email: string, name: string, otp: string) {
    try {
      await send(
        email,
        'Your TaskManagement verification code',
        wrap(`
          <h2 style="color:#111827;margin-top:0;">Verify your email</h2>
          <p style="color:#374151;">Hi <strong>${name}</strong>, use the code below to verify your email address.</p>
          <div style="background:#f3f4f6;border-radius:8px;padding:24px;text-align:center;margin:24px 0;">
            <span style="font-size:40px;font-weight:800;letter-spacing:12px;color:#6366f1;">${otp}</span>
          </div>
          <p style="color:#6b7280;font-size:14px;">
            This code expires in <strong>10 minutes</strong>. Do not share it with anyone.
          </p>
        `)
      );
    } catch (err) {
      logger.error('sendOtpEmail failed:', err);
    }
  },

  async sendPasswordResetEmail(email: string, name: string, token: string) {
    const resetUrl = `${config.clientUrl}/reset-password?token=${token}&email=${encodeURIComponent(email)}`;
    try {
      await send(
        email,
        'Reset your TaskManagement password',
        wrap(`
          <h2 style="color:#111827;margin-top:0;">Reset your password</h2>
          <p style="color:#374151;">Hi <strong>${name}</strong>, we received a request to reset your password.</p>
          <div style="margin:24px 0;">
            <a href="${resetUrl}"
               style="background:#6366f1;color:white;padding:14px 28px;text-decoration:none;
                      border-radius:8px;display:inline-block;font-weight:600;font-size:15px;">
              Reset Password
            </a>
          </div>
          <p style="color:#6b7280;font-size:14px;">
            This link expires in <strong>1 hour</strong>. If you didn't request this, ignore this email.
          </p>
          <p style="color:#9ca3af;font-size:12px;word-break:break-all;">Or copy: ${resetUrl}</p>
        `)
      );
    } catch (err) {
      logger.error('sendPasswordResetEmail failed:', err);
    }
  },

  async sendPasswordChangedEmail(email: string, name: string) {
    try {
      await send(
        email,
        'Your TaskManagement password was changed',
        wrap(`
          <h2 style="color:#111827;margin-top:0;">Password changed</h2>
          <p style="color:#374151;">Hi <strong>${name}</strong>, your password was successfully changed.</p>
          <p style="color:#374151;">
            If you didn't do this,
            <a href="${config.clientUrl}/forgot-password" style="color:#6366f1;">reset your password immediately</a>.
          </p>
        `)
      );
    } catch (err) {
      logger.error('sendPasswordChangedEmail failed:', err);
    }
  },

  async sendNotificationEmail(email: string, subject: string, message: string) {
    try {
      await send(email, subject, wrap(`<p style="color:#374151;">${message}</p>`));
    } catch (err) {
      logger.error('sendNotificationEmail failed:', err);
    }
  },
};

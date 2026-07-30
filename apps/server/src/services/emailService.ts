import sgMail from '@sendgrid/mail';
import { config } from '../config';
import { logger } from '../utils/logger';

// ── SendGrid HTTPS API ────────────────────────────────────────────────────────
let initialized = false;

const getClient = (): boolean => {
  if (initialized) return true;
  const key = process.env.SENDGRID_API_KEY;
  if (!key) {
    logger.warn('SENDGRID_API_KEY not set — emails will not be sent');
    return false;
  }
  sgMail.setApiKey(key);
  initialized = true;
  logger.info('SendGrid client initialized');
  return true;
};

const FROM_EMAIL = process.env.SENDGRID_FROM_EMAIL || 'ramyasribalivada@gmail.com';
const FROM_NAME  = 'TaskManagement';

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

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// ── Core send ─────────────────────────────────────────────────────────────────
const send = async (
  to: string,
  subject: string,
  html: string,
  attachments?: Array<{ content: string; filename: string; type: string; disposition: string }>
): Promise<void> => {
  if (!getClient()) {
    logger.warn(`Email skipped — SendGrid not configured. To: ${to}`);
    return;
  }
  logger.info(`Sending email via SendGrid to: ${to}`);
  await sgMail.send({
    to,
    from: { email: FROM_EMAIL, name: FROM_NAME },
    subject,
    html,
    ...(attachments ? { attachments } : {}),
  });
  logger.info(`Email sent via SendGrid to: ${to}`);
};

// ── Build Google Calendar quick-add URL ───────────────────────────────────────
function buildGoogleCalUrl(event: {
  title: string; description?: string; location?: string;
  start: Date; end: Date; allDay?: boolean;
}): string {
  const fmt = (d: Date) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const dates = event.allDay
    ? `${fmt(event.start).slice(0, 8)}/${fmt(event.end).slice(0, 8)}`
    : `${fmt(event.start)}/${fmt(event.end)}`;
  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: event.title,
    dates,
    ...(event.description ? { details: event.description } : {}),
    ...(event.location ? { location: event.location } : {}),
  });
  return `https://calendar.google.com/calendar/render?${params.toString()}`;
}

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

  async sendNotificationEmail(email: string, subject: string, htmlBody: string) {
    try {
      const isHtml = htmlBody.trim().startsWith('<');
      await send(email, subject, isHtml ? wrap(htmlBody) : wrap(`<p style="color:#374151;">${htmlBody}</p>`));
    } catch (err) {
      logger.error('sendNotificationEmail failed:', err);
    }
  },

  /**
   * Send a calendar invite with .ics attachment + Google Calendar quick-add link.
   * The .ics file sets a 15-min reminder automatically.
   */
  async sendCalendarInvite(
    email: string,
    name: string,
    event: {
      title: string;
      description?: string;
      location?: string;
      start: Date;
      end: Date;
      allDay?: boolean;
      url?: string;
    }
  ) {
    try {
      const { buildICS } = await import('../utils/icsBuilder');
      const icsContent = buildICS({
        ...event,
        organizer: { name: FROM_NAME, email: FROM_EMAIL },
        reminderMinutes: 15,
      });

      const startStr = event.allDay
        ? event.start.toDateString()
        : event.start.toLocaleString('en-US', {
            weekday: 'short', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit',
          });
      const endStr = event.allDay
        ? ''
        : ` – ${event.end.toLocaleString('en-US', { hour: '2-digit', minute: '2-digit' })}`;

      const googleUrl = buildGoogleCalUrl(event);
      const viewUrl = event.url || `${config.clientUrl}/calendar`;

      await send(
        email,
        `📅 Calendar Invite: ${event.title}`,
        wrap(`
          <h2 style="color:#111827;margin-top:0;">New Event: ${escapeHtml(event.title)}</h2>
          <p style="color:#374151;">Hi <strong>${escapeHtml(name)}</strong>, a new event has been scheduled for you.</p>

          <div style="background:#f3f4f6;border-radius:8px;padding:20px;margin:16px 0;">
            <table style="border-collapse:collapse;width:100%;">
              <tr><td style="padding:4px 0;color:#6b7280;width:80px;">📅 When</td>
                  <td style="padding:4px 0;color:#111827;font-weight:500;">${escapeHtml(startStr)}${endStr}</td></tr>
              ${event.location ? `<tr><td style="padding:4px 0;color:#6b7280;">📍 Where</td>
                  <td style="padding:4px 0;color:#111827;">${escapeHtml(event.location)}</td></tr>` : ''}
              ${event.description ? `<tr><td style="padding:4px 0;color:#6b7280;vertical-align:top;">📝 Notes</td>
                  <td style="padding:4px 0;color:#111827;">${escapeHtml(event.description)}</td></tr>` : ''}
            </table>
          </div>

          <div style="margin:24px 0;">
            <a href="${googleUrl}"
               style="background:#4285f4;color:white;padding:12px 20px;text-decoration:none;
                      border-radius:8px;display:inline-block;font-weight:600;font-size:14px;margin-right:12px;">
              + Add to Google Calendar
            </a>
            <a href="${viewUrl}"
               style="background:#6366f1;color:white;padding:12px 20px;text-decoration:none;
                      border-radius:8px;display:inline-block;font-weight:600;font-size:14px;">
              View in App
            </a>
          </div>

          <p style="color:#6b7280;font-size:13px;">
            A <strong>calendar file (.ics)</strong> is also attached — open it to add this event to
            Google Calendar, Outlook, or Apple Calendar. A <strong>15-minute reminder</strong> is set automatically.
          </p>
        `),
        [
          {
            content: Buffer.from(icsContent).toString('base64'),
            filename: 'event.ics',
            type: 'text/calendar',
            disposition: 'attachment',
          },
        ]
      );
    } catch (err) {
      logger.error('sendCalendarInvite failed:', err);
    }
  },
};

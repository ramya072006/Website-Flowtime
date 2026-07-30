import { Application } from 'express';
import { Server as SocketServer } from 'socket.io';
import { Notification } from '../models/Notification';
import { User } from '../models/User';
import { emailService } from '../services/emailService';
import { config } from '../config';
import { logger } from './logger';

interface NotifyOptions {
  userId: string;
  type: string;
  title: string;
  message: string;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
  app?: Application;
  sendEmail?: boolean; // default true — send email if user has email notifications enabled
}

/**
 * Save notification to DB, push via WebSocket, and email the user.
 * Always fire-and-forget — never throws.
 */
export const notify = async (opts: NotifyOptions): Promise<void> => {
  try {
    // 1. Save to DB
    const notification = await Notification.create({
      userId: opts.userId,
      type: opts.type,
      title: opts.title,
      message: opts.message,
      actionUrl: opts.actionUrl,
      metadata: opts.metadata,
    });

    // 2. Push via WebSocket
    if (opts.app) {
      const io: SocketServer | undefined = opts.app.get('io');
      if (io) {
        io.to(`user:${opts.userId}`).emit('notification:new', notification.toObject());
      }
    }

    // 3. Send email (non-blocking, only if user has email notifications enabled)
    if (opts.sendEmail !== false) {
      setImmediate(async () => {
        try {
          const user = await User.findById(opts.userId).select('email name notificationSettings');
          if (!user) return;
          if (user.notificationSettings?.email === false) return; // user disabled email notifs

          const actionUrl = opts.actionUrl
            ? `${config.clientUrl}${opts.actionUrl}`
            : config.clientUrl;

          await emailService.sendNotificationEmail(
            user.email,
            opts.title,
            buildEmailBody(user.name, opts.title, opts.message, actionUrl)
          );
        } catch (err) {
          logger.error('notify() email send failed:', err);
        }
      });
    }
  } catch (err) {
    logger.error('notify() failed:', err);
  }
};

// ── Build a clean HTML email body ─────────────────────────────────────────────
function buildEmailBody(name: string, title: string, message: string, actionUrl: string): string {
  return `
    <h2 style="color:#111827;margin-top:0;">${title}</h2>
    <p style="color:#374151;">Hi <strong>${name}</strong>,</p>
    <p style="color:#374151;">${message}</p>
    <div style="margin:24px 0;">
      <a href="${actionUrl}"
         style="background:#6366f1;color:white;padding:12px 24px;text-decoration:none;
                border-radius:8px;display:inline-block;font-weight:600;font-size:14px;">
        View in TaskManagement →
      </a>
    </div>
    <p style="color:#9ca3af;font-size:12px;">
      You're receiving this because you have email notifications enabled.
      <a href="${config.clientUrl}/settings" style="color:#6366f1;">Manage preferences</a>
    </p>
  `;
}

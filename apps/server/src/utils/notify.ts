import { Application } from 'express';
import { Server as SocketServer } from 'socket.io';
import { Notification } from '../models/Notification';
import { logger } from './logger';

interface NotifyOptions {
  userId: string;
  type: string;
  title: string;
  message: string;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
  app?: Application; // pass req.app to emit via socket
}

/**
 * Save a notification to DB and push it to the user via WebSocket.
 * Always fire-and-forget — never throws.
 */
export const notify = async (opts: NotifyOptions): Promise<void> => {
  try {
    const notification = await Notification.create({
      userId: opts.userId,
      type: opts.type,
      title: opts.title,
      message: opts.message,
      actionUrl: opts.actionUrl,
      metadata: opts.metadata,
    });

    // Push via socket if app is provided
    if (opts.app) {
      const io: SocketServer | undefined = opts.app.get('io');
      if (io) {
        io.to(`user:${opts.userId}`).emit('notification:new', notification.toObject());
      }
    }
  } catch (err) {
    logger.error('notify() failed:', err);
  }
};

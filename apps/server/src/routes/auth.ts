import { Router, RequestHandler } from 'express';
import { authController } from '../controllers/authController';
import { authenticate } from '../middlewares/auth';
import { emailService } from '../services/emailService';
import { sendSuccess, sendError } from '../utils/apiResponse';
import { logger } from '../utils/logger';

const router = Router();

// ── TEST EMAIL ENDPOINT (remove after confirming email works) ─────────────────
router.get('/test-email', async (req, res) => {
  const to = (req.query.to as string) || 'ramyasribalivada@gmail.com';
  logger.info(`Test email requested to: ${to}`);
  logger.info(`RESEND_API_KEY=${process.env.RESEND_API_KEY ? 'SET (' + process.env.RESEND_API_KEY.slice(0, 8) + '...)' : 'MISSING'}`);
  logger.info(`BREVO_API_KEY=${process.env.BREVO_API_KEY ? 'SET' : 'MISSING'}`);
  try {
    await emailService.sendOtpEmail(to, 'Test User', '123456');
    sendSuccess(res, { to }, 'Test email sent — check inbox and Render logs');
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    logger.error('Test email failed:', err);
    sendError(res, `Email failed: ${message}`, 500);
  }
});

// Public routes
router.post('/register',         authController.register        as RequestHandler);
router.post('/verify-otp',       authController.verifyOtp       as RequestHandler);
router.post('/resend-otp',       authController.resendOtp       as RequestHandler);
router.post('/login',            authController.login           as RequestHandler);
router.post('/forgot-password',  authController.forgotPassword  as RequestHandler);
router.post('/reset-password',   authController.resetPassword   as RequestHandler);
router.post('/refresh',          authController.refreshToken    as RequestHandler);

// Protected routes
router.post('/logout',           authenticate as RequestHandler, authController.logout         as RequestHandler);
router.get('/me',                authenticate as RequestHandler, authController.getMe          as RequestHandler);
router.patch('/profile',         authenticate as RequestHandler, authController.updateProfile  as RequestHandler);
router.patch('/change-password', authenticate as RequestHandler, authController.changePassword as RequestHandler);

export default router;

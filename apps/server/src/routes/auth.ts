import { Router, RequestHandler } from 'express';
import { authController } from '../controllers/authController';
import { authenticate } from '../middlewares/auth';

const router = Router();

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

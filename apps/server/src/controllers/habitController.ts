import { Response } from 'express';
import { habitService } from '../services/habitService';
import { sendSuccess, sendCreated } from '../utils/apiResponse';
import { asyncHandler } from '../utils/asyncHandler';
import { AuthRequest } from '../middlewares/auth';
import { notify } from '../utils/notify';

export const habitController = {
  getHabits: asyncHandler(async (req: AuthRequest, res: Response) => {
    const habits = await habitService.getHabits(req.user!.userId);
    sendSuccess(res, habits);
  }),

  getHabit: asyncHandler(async (req: AuthRequest, res: Response) => {
    const habit = await habitService.getHabitById(req.params.id as string, req.user!.userId);
    sendSuccess(res, habit);
  }),

  createHabit: asyncHandler(async (req: AuthRequest, res: Response) => {
    const habit = await habitService.createHabit(req.user!.userId, req.body);
    sendCreated(res, habit, 'Habit created');
    notify({
      userId: req.user!.userId,
      type: 'habit_reminder',
      title: 'New Habit Created 🎯',
      message: `"${habit.title}" has been added to your habits.`,
      actionUrl: '/habits',
      app: req.app,
    });
  }),

  updateHabit: asyncHandler(async (req: AuthRequest, res: Response) => {
    const habit = await habitService.updateHabit(req.params.id as string, req.user!.userId, req.body);
    sendSuccess(res, habit, 'Habit updated');
  }),

  deleteHabit: asyncHandler(async (req: AuthRequest, res: Response) => {
    await habitService.deleteHabit(req.params.id as string, req.user!.userId);
    sendSuccess(res, null, 'Habit deleted');
  }),

  logCompletion: asyncHandler(async (req: AuthRequest, res: Response) => {
    const { completed, duration, notes } = req.body;
    const habit = await habitService.logCompletion(
      req.params.id as string, req.user!.userId, completed, duration, notes
    );
    sendSuccess(res, habit, 'Completion logged');
    if (completed) {
      notify({
        userId: req.user!.userId,
        type: 'habit_reminder',
        title: `🔥 Habit Completed!`,
        message: `"${habit.title}" done! ${habit.streak > 1 ? `${habit.streak} day streak! 🔥` : 'Keep it up!'}`,
        actionUrl: '/habits',
        app: req.app,
      });
    }
  }),

  getMetrics: asyncHandler(async (req: AuthRequest, res: Response) => {
    const metrics = await habitService.getHabitMetrics(req.params.id as string, req.user!.userId);
    sendSuccess(res, metrics);
  }),

  getTodayHabits: asyncHandler(async (req: AuthRequest, res: Response) => {
    const habits = await habitService.getTodayHabits(req.user!.userId);
    sendSuccess(res, habits);
  }),
};

import crypto from 'crypto';

interface ICSEvent {
  uid?: string;
  title: string;
  description?: string;
  location?: string;
  start: Date;
  end: Date;
  allDay?: boolean;
  organizer?: { name: string; email: string };
  reminderMinutes?: number; // default 15 min before
  url?: string;
}

/**
 * Build a standard .ics (iCalendar) string for a single event.
 * Works with Google Calendar, Apple Calendar, Outlook — any compliant client.
 */
export function buildICS(event: ICSEvent): string {
  const uid = event.uid || `${crypto.randomUUID()}@taskmanagement`;
  const now = formatDate(new Date());
  const reminder = event.reminderMinutes ?? 15;

  const lines: string[] = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//TaskManagement//TaskManagement//EN',
    'CALSCALE:GREGORIAN',
    'METHOD:REQUEST',
    'BEGIN:VEVENT',
    `UID:${uid}`,
    `DTSTAMP:${now}`,
    `DTSTART:${event.allDay ? formatDateOnly(event.start) : formatDate(event.start)}`,
    `DTEND:${event.allDay ? formatDateOnly(event.end) : formatDate(event.end)}`,
    `SUMMARY:${escapeICS(event.title)}`,
  ];

  if (event.description) {
    lines.push(`DESCRIPTION:${escapeICS(event.description)}`);
  }
  if (event.location) {
    lines.push(`LOCATION:${escapeICS(event.location)}`);
  }
  if (event.url) {
    lines.push(`URL:${event.url}`);
  }
  if (event.organizer) {
    lines.push(`ORGANIZER;CN=${event.organizer.name}:MAILTO:${event.organizer.email}`);
  }

  // Add a reminder alarm
  lines.push(
    'BEGIN:VALARM',
    'ACTION:DISPLAY',
    `DESCRIPTION:Reminder: ${escapeICS(event.title)}`,
    `TRIGGER:-PT${reminder}M`,
    'END:VALARM'
  );

  lines.push('END:VEVENT', 'END:VCALENDAR');

  return lines.join('\r\n');
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatDate(d: Date): string {
  return d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
}

function formatDateOnly(d: Date): string {
  return d.toISOString().slice(0, 10).replace(/-/g, '');
}

function escapeICS(str: string): string {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '');
}

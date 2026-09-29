import { BookOpen, Clock, Calendar } from 'lucide-react';

export default function BookingsPage() {
  return (
    <div style={{
      maxWidth: 1280, margin: '0 auto',
      padding: '3rem 1.5rem',
      minHeight: 'calc(100vh - 64px)',
    }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>My Bookings</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Track and manage all your villa reservations.</p>
      </div>

      {/* Empty State */}
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', textAlign: 'center',
        padding: '5rem 2rem',
        background: 'var(--surface)',
        borderRadius: 'var(--radius-xl)',
        border: '1px solid var(--border)',
      }}>
        <div style={{
          width: 60, height: 60, borderRadius: '50%',
          background: 'var(--accent-light)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginBottom: '1.25rem',
        }}>
          <BookOpen size={26} color="var(--accent)" strokeWidth={2} />
        </div>
        <h3 style={{ fontWeight: 700, fontSize: '1.125rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          No reservations yet
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', maxWidth: 340, marginBottom: '2rem' }}>
          Once you book a villa, your reservations will appear here so you can track and manage them.
        </p>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.5rem 0.875rem',
            background: 'var(--surface-2)',
            borderRadius: 8, fontSize: '0.85rem', color: 'var(--text-secondary)',
          }}>
            <Calendar size={14} strokeWidth={2} /> Flexible dates
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.5rem 0.875rem',
            background: 'var(--surface-2)',
            borderRadius: 8, fontSize: '0.85rem', color: 'var(--text-secondary)',
          }}>
            <Clock size={14} strokeWidth={2} /> Instant confirmation
          </div>
        </div>
      </div>
    </div>
  );
}

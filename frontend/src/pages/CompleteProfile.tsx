import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import axios from 'axios';
import { authService, type CompleteProfileData } from '../api/authService';
import { getNames } from 'country-list';
import { User, Phone, Calendar, MapPin, Globe, ChevronRight } from 'lucide-react';

const COUNTRIES = getNames();

const STEPS = [
  { label: 'Personal', icon: User },
  { label: 'Contact',  icon: Phone },
  { label: 'Location', icon: Globe },
];

export default function CompleteProfile() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState<CompleteProfileData>({
    phone_number: '',
    date_of_birth: '',
    city: '',
    country: '',
    gender: 'Male',
  });

  const update = (key: keyof CompleteProfileData, value: string) =>
    setFormData(prev => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await authService.completeProfile(formData);
      toast.success('Profile completed! Welcome aboard 🎉');
      navigate('/');
    } catch (err) {
      if (axios.isAxiosError(err)) {
        toast.error(err.response?.data?.detail || 'Validation failed.');
      } else {
        toast.error('Something went wrong.');
      }
    } finally { setIsLoading(false); }
  };

  const inputStyle = {
    width: '100%', padding: '0.75rem 1rem 0.75rem 2.75rem',
    fontFamily: 'Inter, sans-serif', fontSize: '0.9375rem',
    color: 'var(--text-primary)',
    background: 'var(--surface)',
    border: '1.5px solid var(--border)',
    borderRadius: 'var(--radius-md)',
    outline: 'none', transition: 'border-color 0.15s, box-shadow 0.15s',
  };

  const iconWrap = {
    position: 'absolute' as const, left: '0.875rem', top: '50%',
    transform: 'translateY(-50%)',
    color: 'var(--text-muted)', display: 'flex', pointerEvents: 'none' as const,
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', padding: '2rem 1rem',
    }}>
      <div style={{ width: '100%', maxWidth: 500 }} className="animate-fade-in">
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 56, height: 56, borderRadius: '50%',
            background: 'var(--accent-light)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1rem',
          }}>
            <User size={24} color="var(--accent)" strokeWidth={2} />
          </div>
          <h1 style={{ fontSize: '1.625rem', marginBottom: '0.375rem' }}>Almost there!</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Complete your profile to start booking</p>
        </div>

        {/* Step indicator */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
          {STEPS.map((s, i) => {
            const done = i < step;
            const active = i === step;
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: done || active ? 'var(--accent)' : 'var(--surface)',
                    border: `2px solid ${done || active ? 'var(--accent)' : 'var(--border)'}`,
                    fontSize: '0.75rem', fontWeight: 700,
                    color: done || active ? '#fff' : 'var(--text-muted)',
                    transition: 'all 0.2s',
                  }}>
                    {done ? '✓' : i + 1}
                  </div>
                  <span style={{ fontSize: '0.8rem', fontWeight: active ? 600 : 400, color: active ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                    {s.label}
                  </span>
                </div>
                {i < STEPS.length - 1 && (
                  <div style={{ width: 32, height: 2, background: i < step ? 'var(--accent)' : 'var(--border)', borderRadius: 2, transition: 'background 0.2s' }} />
                )}
              </div>
            );
          })}
        </div>

        {/* Form card */}
        <div className="card" style={{ padding: '2rem' }}>
          <form onSubmit={handleSubmit}>

            {/* Step 0: Personal */}
            {step === 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }} className="animate-fade-in">
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.25rem' }}>Personal information</h3>

                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.375rem' }}>Date of birth</label>
                  <div style={{ position: 'relative' }}>
                    <span style={iconWrap}><Calendar size={16} strokeWidth={2} /></span>
                    <input type="date" required style={inputStyle}
                      value={formData.date_of_birth}
                      onChange={e => update('date_of_birth', e.target.value)}
                      onFocus={e => { (e.target as HTMLElement).style.borderColor = 'var(--border-focus)'; (e.target as HTMLElement).style.boxShadow = '0 0 0 3px rgba(124,58,237,0.12)'; }}
                      onBlur={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; (e.target as HTMLElement).style.boxShadow = 'none'; }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.375rem' }}>Gender</label>
                  <select style={{ ...inputStyle, paddingLeft: '1rem', appearance: 'auto' }}
                    value={formData.gender} onChange={e => update('gender', e.target.value)}
                    onFocus={e => { (e.target as HTMLElement).style.borderColor = 'var(--border-focus)'; }}
                    onBlur={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; }}>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                  </select>
                </div>

                <button type="button" className="btn btn-primary btn-full btn-lg" style={{ marginTop: '0.5rem' }}
                  onClick={() => { if (!formData.date_of_birth) { toast.error('Please select your date of birth'); return; } setStep(1); }}>
                  Continue <ChevronRight size={16} strokeWidth={2.5} />
                </button>
              </div>
            )}

            {/* Step 1: Contact */}
            {step === 1 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }} className="animate-fade-in">
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.25rem' }}>Contact details</h3>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.375rem' }}>Phone number</label>
                  <div style={{ position: 'relative' }}>
                    <span style={iconWrap}><Phone size={16} strokeWidth={2} /></span>
                    <input type="tel" required style={inputStyle} placeholder="+1 234 567 8900"
                      value={formData.phone_number} onChange={e => update('phone_number', e.target.value)}
                      onFocus={e => { (e.target as HTMLElement).style.borderColor = 'var(--border-focus)'; (e.target as HTMLElement).style.boxShadow = '0 0 0 3px rgba(124,58,237,0.12)'; }}
                      onBlur={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; (e.target as HTMLElement).style.boxShadow = 'none'; }}
                    />
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.875rem' }}>
                  <button type="button" className="btn btn-secondary btn-lg" style={{ flex: '0 0 auto' }} onClick={() => setStep(0)}>
                    Back
                  </button>
                  <button type="button" className="btn btn-primary btn-full btn-lg"
                    onClick={() => { if (!formData.phone_number) { toast.error('Please enter a phone number'); return; } setStep(2); }}>
                    Continue <ChevronRight size={16} strokeWidth={2.5} />
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Location */}
            {step === 2 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }} className="animate-fade-in">
                <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.25rem' }}>Your location</h3>

                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.375rem' }}>City</label>
                  <div style={{ position: 'relative' }}>
                    <span style={iconWrap}><MapPin size={16} strokeWidth={2} /></span>
                    <input type="text" required style={inputStyle} placeholder="Paris"
                      value={formData.city} onChange={e => update('city', e.target.value)}
                      onFocus={e => { (e.target as HTMLElement).style.borderColor = 'var(--border-focus)'; (e.target as HTMLElement).style.boxShadow = '0 0 0 3px rgba(124,58,237,0.12)'; }}
                      onBlur={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; (e.target as HTMLElement).style.boxShadow = 'none'; }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.375rem' }}>Country</label>
                  <div style={{ position: 'relative' }}>
                    <span style={iconWrap}><Globe size={16} strokeWidth={2} /></span>
                    <select required style={{ ...inputStyle, paddingLeft: '2.75rem', appearance: 'auto' }}
                      value={formData.country} onChange={e => update('country', e.target.value)}
                      onFocus={e => { (e.target as HTMLElement).style.borderColor = 'var(--border-focus)'; }}
                      onBlur={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; }}>
                      <option value="" disabled>Select your country</option>
                      {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.875rem', marginTop: '0.5rem' }}>
                  <button type="button" className="btn btn-secondary btn-lg" style={{ flex: '0 0 auto' }} onClick={() => setStep(1)}>
                    Back
                  </button>
                  <button type="submit" disabled={isLoading} className="btn btn-primary btn-full btn-lg">
                    {isLoading ? 'Saving…' : 'Complete profile ✦'}
                  </button>
                </div>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
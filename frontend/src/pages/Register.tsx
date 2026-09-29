import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { GoogleLogin } from '@react-oauth/google';
import { authService } from '../api/authService';
import { Eye, EyeOff, Home } from 'lucide-react';

export default function Register() {
  const [firstName, setFirstName] = useState('');
  const [lastName,  setLastName]  = useState('');
  const [email,     setEmail]     = useState('');
  const [password,  setPassword]  = useState('');
  const [showPw,    setShowPw]    = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) { toast.error('Password must be at least 8 characters'); return; }
    setIsLoading(true);
    try {
      await authService.register({
        first_name: firstName,
        last_name:  lastName,
        email,
        password,
        phone_number: '',
        date_of_birth: '',
        gender: '',
        location: '',
      });
      const loginData = await authService.login(email, password);
      localStorage.setItem('token', loginData.access_token);
      toast.success('Account created! Complete your profile.');
      navigate('/complete-profile');
    } catch {
      toast.error('Failed to create account. Email might already be in use.');
    } finally { setIsLoading(false); }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    try {
      const data = await authService.googleLogin(credentialResponse.credential);
      localStorage.setItem('token', data.access_token);
      toast.success('Google account connected!');
      navigate(data.requires_onboarding ? '/complete-profile' : '/');
    } catch { toast.error('Google authentication failed'); }
    finally { setIsLoading(false); }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      background: 'var(--bg)',
    }}>
      {/* Left Brand Panel */}
      <div style={{
        background: 'linear-gradient(150deg, #1A0533 0%, #2D1065 50%, #4C1D95 100%)',
        display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        padding: '2.5rem', position: 'relative', overflow: 'hidden',
      }} className="auth-brand-panel">
        <div style={{ position:'absolute',width:450,height:450,borderRadius:'50%',top:'-120px',right:'-100px',background:'radial-gradient(circle,rgba(124,58,237,0.4) 0%,transparent 70%)',pointerEvents:'none' }}/>
        <div style={{ position:'absolute',width:300,height:300,borderRadius:'50%',bottom:'-60px',left:'-80px',background:'radial-gradient(circle,rgba(192,132,252,0.25) 0%,transparent 70%)',pointerEvents:'none' }}/>

        <div style={{ display:'flex', alignItems:'center', gap:'0.5rem', position:'relative' }}>
          <div style={{ width:36,height:36,borderRadius:10,background:'rgba(255,255,255,0.15)',backdropFilter:'blur(8px)',display:'flex',alignItems:'center',justifyContent:'center',border:'1px solid rgba(255,255,255,0.2)' }}>
            <Home size={18} color="#fff" strokeWidth={2.5} />
          </div>
          <span style={{ fontWeight:800, fontSize:'1.2rem', color:'#fff', letterSpacing:'-0.03em' }}>
            Villa<span style={{ color:'#C084FC' }}>Stay</span>
          </span>
        </div>

        <div style={{ position:'relative' }}>
          <p style={{ color:'rgba(196,181,253,0.8)', fontSize:'0.8rem', fontWeight:600, letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:'1rem' }}>
            Join today
          </p>
          <h2 style={{ color:'#fff', fontSize:'clamp(1.75rem,3vw,2.5rem)', lineHeight:1.2, letterSpacing:'-0.03em', marginBottom:'1rem', fontWeight:800 }}>
            Your next adventure<br/>
            <span style={{ color:'#C084FC' }}>starts here</span>
          </h2>
          <p style={{ color:'rgba(255,255,255,0.55)', fontSize:'1rem', lineHeight:1.6 }}>
            Create your free account and start exploring the world's most beautiful villa rentals.
          </p>
        </div>

        <p style={{ color:'rgba(255,255,255,0.3)', fontSize:'0.8rem', position:'relative' }}>
          © 2026 VillaStay
        </p>
      </div>

      {/* Right Form Panel */}
      <div style={{
        display:'flex', flexDirection:'column', justifyContent:'center', alignItems:'center',
        padding:'2.5rem',
        background:'var(--surface)',
        overflowY:'auto',
      }}>
        <div style={{ width:'100%', maxWidth:400 }} className="animate-fade-in">
          <h1 style={{ fontSize:'1.75rem', marginBottom:'0.375rem' }}>Create account</h1>
          <p style={{ color:'var(--text-secondary)', marginBottom:'2rem' }}>Start your journey with VillaStay</p>

          <form onSubmit={handleRegister} style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.875rem' }}>
              <div>
                <label style={{ display:'block', fontSize:'0.875rem', fontWeight:600, color:'var(--text-primary)', marginBottom:'0.375rem' }}>First name</label>
                <input type="text" required className="input" placeholder="Jane"
                  value={firstName} onChange={e => setFirstName(e.target.value)} disabled={isLoading} />
              </div>
              <div>
                <label style={{ display:'block', fontSize:'0.875rem', fontWeight:600, color:'var(--text-primary)', marginBottom:'0.375rem' }}>Last name</label>
                <input type="text" required className="input" placeholder="Doe"
                  value={lastName} onChange={e => setLastName(e.target.value)} disabled={isLoading} />
              </div>
            </div>

            <div>
              <label style={{ display:'block', fontSize:'0.875rem', fontWeight:600, color:'var(--text-primary)', marginBottom:'0.375rem' }}>Email address</label>
              <input type="email" required className="input" placeholder="you@example.com"
                value={email} onChange={e => setEmail(e.target.value)} disabled={isLoading} />
            </div>

            <div>
              <label style={{ display:'block', fontSize:'0.875rem', fontWeight:600, color:'var(--text-primary)', marginBottom:'0.375rem' }}>Password</label>
              <div style={{ position:'relative' }}>
                <input type={showPw ? 'text' : 'password'} required className="input"
                  placeholder="Min. 8 characters" style={{ paddingRight:'3rem' }}
                  value={password} onChange={e => setPassword(e.target.value)} disabled={isLoading} />
                <button type="button" onClick={() => setShowPw(!showPw)} style={{
                  position:'absolute', right:'0.875rem', top:'50%', transform:'translateY(-50%)',
                  background:'none', border:'none', cursor:'pointer', color:'var(--text-muted)', display:'flex',
                }}>
                  {showPw ? <EyeOff size={17} strokeWidth={2} /> : <Eye size={17} strokeWidth={2} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={isLoading} className="btn btn-primary btn-full btn-lg" style={{ marginTop:'0.375rem' }}>
              {isLoading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <div className="divider" style={{ margin:'1.5rem 0' }}>or</div>

          <div style={{ display:'flex', justifyContent:'center' }}>
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => toast.error('Google login failed')}
              theme="outline" shape="rectangular" width="400" text="signup_with"
            />
          </div>

          <p style={{ textAlign:'center', fontSize:'0.9rem', color:'var(--text-secondary)', marginTop:'1.75rem' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ fontWeight:600, color:'var(--accent)' }}>Sign in</Link>
          </p>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .auth-brand-panel { display: none !important; }
          div[style*="gridTemplateColumns: 1fr 1fr"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
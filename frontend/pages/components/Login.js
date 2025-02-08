import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from './Login.module.css';
import Head from 'next/head';
import { useSignInWithEmailAndPassword } from 'react-firebase-hooks/auth';
import { auth } from '../firebase/config';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { useAuthState } from 'react-firebase-hooks/auth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errMsg, setErrMsg] = useState('');

  
  const [user, loading, error] = useSignInWithEmailAndPassword(auth);
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrMsg(''); 
    

    try {
      const res = await signInWithEmailAndPassword(auth, email, password);  
      router.push('/components/SchoolConfig');
    }
    catch (e) {
      if(e.message === 'Firebase: Error (auth/missing-password).') {
        setErrMsg('Please enter a password.');
      } else if(e.message === 'Firebase: Error (auth/invalid-email).') {
        setErrMsg('Please enter a valid email address.');
      } else if(e.message === 'Firebase: Error (auth/invalid-credential).') {
        setErrMsg('Invalid credentials. Please try again.');
      }
    }
  };

  useEffect(() => {
    if (error) {
      switch (error.code) {
        case 'auth/user-not-found':
          setErrMsg('No account found with this email.');
          break;
        case 'auth/wrong-password':
          setErrMsg('Incorrect password.');
          break;
        case 'auth/invalid-email':
          setErrMsg('Please enter a valid email address.');
          break;
        default:
          setErrMsg('An error occurred. Please try again.');
          break;
      }
    }
  }, [error]);

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className={styles.loginBody}>
        <div className={styles.wrapper}>
          <div className={styles.inner}>
            <div className={styles.formStyle}>
              <h3 className={styles.headingStyle}>Login to Your Account</h3>

              <div className={styles.formWrapper}>
                <label className={styles.labelStyle}>
                  <i className="fas fa-envelope"></i> Email
                </label>
                <input
                  type="email"
                  className={`${styles.inputStyle} ${styles.formControl}`}
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className={styles.formWrapper}>
                <label className={styles.labelStyle}>
                  <i className="fas fa-lock"></i> Password
                </label>
                <input
                  type="password"
                  className={`${styles.inputStyle} ${styles.formControl}`}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className={styles.forgotPassword}>
                <Link href="/forgot-password">
                  Forgot password?
                </Link>
              </div>

              <button className={styles.buttonStyle} disabled={loading} onClick={handleLogin}>
                {loading ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-sign-in-alt"></i>} Login
              </button>

              {errMsg && (
                <div className={styles.errorBox}>
                  <p>{errMsg}</p>
                </div>
              )}

            {loading && <p className={styles.loadingText}>Loading...</p>}
            
              <div className={styles.separator}>
                <span className={styles.separatorText}>OR</span>
              </div>

              <div className={styles.googleButton}>
                <button className={styles.googleButtonStyle}>
                  <i className="fab fa-google"></i> Sign In with Google
                </button>
              </div>

              <p className={styles.registerText}>
                Don’t have an account? <Link href="/components/Signup" className={styles.linkText}>Sign Up</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

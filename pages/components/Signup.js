import React, { useState, useEffect } from 'react';
import styles from './Signup.module.css';
import Head from 'next/head';
import Link from 'next/link';
import { useCreateUserWithEmailAndPassword } from 'react-firebase-hooks/auth';
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { auth } from '../firebase/config';

export default function Signup() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errMsg, setErrMsg] = useState('');
  const [createUserWithEmailAndPassword, user, loading, error] =
    useCreateUserWithEmailAndPassword(auth);

  const firebaseErrorMessages = {
    'auth/email-already-in-use': 'This email address is already in use. Please try logging in.',
    'auth/weak-password': 'Password should be at least 6 characters long.',
    'auth/invalid-email': 'Please enter a valid email address.',
    default: 'An error occurred. Please try again.',
  };

  const handleSignUp = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setErrMsg('Passwords do not match.');
      return;
    }

    try {
      await createUserWithEmailAndPassword(email, password);

      setFirstName('');
      setLastName('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setErrMsg('');
    } catch (err) {
      console.error('Unexpected Error:', err.message);
    }
  };

  const handleGoogleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      console.log('Google User:', result.user);
    } catch (err) {
      setErrMsg('Failed to sign in with Google.');
    }
  };

  useEffect(() => {
    if (error) {
      const errorMessage =
        firebaseErrorMessages[error.code] || firebaseErrorMessages.default;
      setErrMsg(errorMessage);
    }
  }, [error]);

  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        />
      </Head>

      <div className={styles.signupBody}>
        <div className={styles.wrapper}>
          <div className={styles.inner}>
            <form className={styles.formStyle} onSubmit={handleSignUp}>
              <h3 className={styles.headingStyle}>Registration Form</h3>

              <div className={styles.formGroup}>
                <div className={styles.formWrapper}>
                  <label className={styles.labelStyle}>
                    <i className="fas fa-user"></i> First Name
                  </label>
                  <input
                    type="text"
                    className={`${styles.inputStyle} ${styles.formControl}`}
                    placeholder="Enter your first name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                  />
                </div>
                <div className={styles.formWrapper}>
                  <label className={styles.labelStyle}>
                    <i className="fas fa-user"></i> Last Name
                  </label>
                  <input
                    type="text"
                    className={`${styles.inputStyle} ${styles.formControl}`}
                    placeholder="Enter your last name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                  />
                </div>
              </div>

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

              <div className={styles.formWrapper}>
                <label className={styles.labelStyle}>
                  <i className="fas fa-lock"></i> Confirm Password
                </label>
                <input
                  type="password"
                  className={`${styles.inputStyle} ${styles.formControl}`}
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>

              <button type="submit" className={styles.buttonStyle}>
                <i className="fas fa-paper-plane"></i> Register Now
              </button>
            </form>

            {errMsg && (
                <div className={styles.errorBox}>
                  <p>{errMsg}</p>
                </div>
              )}

            {loading && <p className={styles.loadingText}>Loading...</p>}


            <div className={styles.separator}>
              <span className={styles.separatorLine}></span>
              <span className={styles.separatorText}>OR</span>
              <span className={styles.separatorLine}></span>
            </div>

            <div className={styles.googleButton}>
              <button
                className={styles.googleButtonStyle}
                onClick={handleGoogleSignIn}
              >
                <i className="fab fa-google"></i> Sign Up with Google
              </button>
            </div>

            <p className={styles.alreadyAccount}>
              Already have an account?{' '}
              <Link href="/components/Login" className={styles.linkText}>
                Login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

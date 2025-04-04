import React, { useState, useEffect } from 'react';
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

      <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-white via-gray-50 to-gray-200 p-0 m-0">
        <div className="w-full flex justify-center items-center">
          <div className="w-full max-w-2xl bg-white p-8 rounded-lg shadow-md">
            <form onSubmit={handleSignUp} className="space-y-6">
              <h3 className="text-2xl text-center text-gray-800 font-bold uppercase tracking-wider mb-8">
                Registration Form
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    <i className="fas fa-user text-red-600 mr-2"></i> First Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 pl-10 rounded-full border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                    placeholder="Enter your first name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    <i className="fas fa-user text-red-600 mr-2"></i> Last Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 pl-10 rounded-full border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                    placeholder="Enter your last name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  <i className="fas fa-envelope text-red-600 mr-2"></i> Email
                </label>
                <input
                  type="email"
                  className="w-full px-4 py-3 pl-10 rounded-full border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  <i className="fas fa-lock text-red-600 mr-2"></i> Password
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-3 pl-10 rounded-full border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  <i className="fas fa-lock text-red-600 mr-2"></i> Confirm Password
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-3 pl-10 rounded-full border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>

              <div className="flex justify-center">
                <button
                  type="submit"
                  className="w-[30%] py-3 px-6 bg-red-600 text-white rounded-full font-semibold flex items-center justify-center hover:bg-red-700 transition-colors duration-300 transform hover:scale-105"
                >
                  <i className="fas fa-paper-plane mr-2"></i> Register Now
                </button>
              </div>
            </form>

            {errMsg && (
              <div className="mt-4 bg-red-50 text-red-600 p-4 rounded-lg text-center font-semibold">
                <p>{errMsg}</p>
              </div>
            )}

            {loading && (
              <p className="mt-4 text-blue-600 text-center font-semibold animate-pulse">
                Loading...
              </p>
            )}

            <div className="flex items-center justify-center my-6">
              <div className="flex-1 border-t border-gray-300"></div>
              <span className="px-4 text-sm font-bold text-gray-700">OR</span>
              <div className="flex-1 border-t border-gray-300"></div>
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleGoogleSignIn}
                className="w-full py-3 px-4 bg-red-500 text-white rounded-lg font-semibold flex items-center justify-center hover:bg-red-600 transition-colors duration-300"
              >
                <i className="fab fa-google mr-2"></i> Sign Up with Google
              </button>
            </div>

            <p className="text-center text-sm text-gray-600 mt-4">
              Already have an account?{' '}
              <Link href="/components/Login" className="text-red-600 hover:underline">
                Login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

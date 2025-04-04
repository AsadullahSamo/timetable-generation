import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
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

      <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-white via-gray-50 to-gray-200 p-0 m-0">
        <div className="w-full flex justify-center items-center">
          <div className="w-full max-w-md bg-white p-10 rounded-lg shadow-md">
            <div className="space-y-6">
              <h3 className="text-2xl text-center text-gray-800 font-semibold">Login to Your Account</h3>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-gray-700">
                  <i className="fas fa-envelope mr-2"></i> Email
                </label>
                <input
                  type="email"
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-bold text-gray-700">
                  <i className="fas fa-lock mr-2"></i> Password
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-600 focus:ring-1 focus:ring-red-600 outline-none transition-colors"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <div className="text-right">
                <Link href="/forgot-password" className="text-sm text-red-600 hover:underline">
                  Forgot password?
                </Link>
              </div>

              <button 
                className="w-full py-3 px-4 bg-red-600 text-white rounded-lg font-bold flex items-center justify-center hover:bg-red-700 transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading} 
                onClick={handleLogin}
              >
                {loading ? (
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                ) : (
                  <i className="fas fa-sign-in-alt mr-2"></i>
                )}
                Login
              </button>

              {errMsg && (
                <div className="bg-red-50 text-red-600 p-3 rounded-lg text-center font-bold">
                  <p>{errMsg}</p>
                </div>
              )}

              {loading && (
                <p className="text-blue-600 text-center font-bold animate-pulse">
                  Loading...
                </p>
              )}
              
              <div className="flex items-center justify-center my-6">
                <div className="flex-1 border-t border-gray-300"></div>
                <span className="px-4 text-sm font-bold text-gray-700">OR</span>
                <div className="flex-1 border-t border-gray-300"></div>
              </div>

              <div className="flex justify-center">
                <button className="w-full py-3 px-4 bg-red-500 text-white rounded-lg font-bold flex items-center justify-center hover:bg-red-600 transition-colors duration-300">
                  <i className="fab fa-google mr-2"></i> Sign In with Google
                </button>
              </div>

              <p className="text-center text-sm text-gray-600">
                Don't have an account?{' '}
                <Link href="/components/Signup" className="text-red-600 hover:underline">
                  Sign Up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';

export function DebugUser() {
  const [user, setUser] = useState<any>(null);
  const supabase = createClient();

  useEffect(() => {
    console.log('🐛 DebugUser component mounted');
    
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      console.log('🐛 Current user from Supabase:', user);
      setUser(user);
    };

    getUser();
  }, [supabase]);

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'yellow', 
      padding: '10px', 
      zIndex: 9999,
      fontSize: '12px',
      border: '1px solid black'
    }}>
      <div><strong>Debug User Info:</strong></div>
      <div>Email: {user?.email || 'No email'}</div>
      <div>ID: {user?.id || 'No ID'}</div>
      <div>Metadata: {JSON.stringify(user?.user_metadata || {})}</div>
    </div>
  );
}
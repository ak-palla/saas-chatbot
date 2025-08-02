import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function POST(request: NextRequest) {
  try {
    console.log('🔊 TTS API: Frontend TTS route called');
    
    // Parse the request body first to get user_email if provided
    const body = await request.json();
    console.log('🔊 TTS API: Request body:', body);
    
    // Get user email from request body or try authentication
    let userEmail = body.user_email;
    
    if (!userEmail) {
      // Try to get user from authorization header
      const authorization = request.headers.get('authorization');
      console.log('🔊 TTS API: Authorization header:', authorization ? 'Present' : 'Missing');
      
      if (authorization) {
        try {
          const { data, error } = await supabase.auth.getUser(authorization.replace('Bearer ', ''));
          if (!error && data.user?.email) {
            userEmail = data.user.email;
            console.log('🔊 TTS API: Got user email from token:', userEmail);
          } else {
            console.error('🔊 TTS API: Token validation failed:', error);
          }
        } catch (error) {
          console.error('🔊 TTS API: Error validating token:', error);
        }
      }
    }
    
    if (!userEmail) {
      console.error('🔊 TTS API: No user email found in request or token');
      return NextResponse.json(
        { error: 'User email required' },
        { status: 400 }
      );
    }

    console.log('🔊 TTS API: Using user email:', userEmail);

    // Validate required fields
    if (!body.text) {
      return NextResponse.json(
        { error: 'Text is required' },
        { status: 400 }
      );
    }

    // Validate and prepare encoding
    const encoding = body.encoding || 'mp3';
    const voice = body.voice || 'aura-asteria-en';
    const speed = body.speed || 1.0;
    const pitch = body.pitch || 1.0;
    
    // Validate encoding
    const validEncodings = ['mp3', 'wav', 'linear16'];
    if (!validEncodings.includes(encoding)) {
      console.error('🔊 TTS API: Invalid encoding:', encoding);
      return NextResponse.json(
        { error: `Invalid encoding. Must be one of: ${validEncodings.join(', ')}` },
        { status: 400 }
      );
    }

    // Prepare the request to backend TTS service
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/voice/tts?user_email=${encodeURIComponent(userEmail)}`;
    
    console.log('🔊 TTS API: Calling backend TTS service:', backendUrl);
    console.log('🔊 TTS API: Encoding:', encoding);

    // Prepare request payload - only include sample_rate for linear16 and wav
    const requestPayload: any = {
      text: body.text,
      voice: voice,
      encoding: encoding,
      speed: speed,
      pitch: pitch
    };
    
    // Only add sample_rate for encodings that support it
    if (encoding === 'linear16' || encoding === 'wav') {
      requestPayload.sample_rate = body.sample_rate || 24000;
      console.log('🔊 TTS API: Including sample_rate:', requestPayload.sample_rate);
    } else {
      console.log('🔊 TTS API: Excluding sample_rate for encoding:', encoding);
    }

    console.log('🔊 TTS API: Request payload:', requestPayload);

    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestPayload)
    });

    console.log('🔊 TTS API: Backend response status:', backendResponse.status);
    console.log('🔊 TTS API: Backend response headers:', Object.fromEntries(backendResponse.headers.entries()));

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('🔊 TTS API: Backend error response:', errorText);
      console.error('🔊 TTS API: Backend error status:', backendResponse.status, backendResponse.statusText);
      
      // Try to parse error as JSON for better error reporting
      let errorMessage = `TTS service failed: ${backendResponse.status} ${backendResponse.statusText}`;
      try {
        const errorJson = JSON.parse(errorText);
        if (errorJson.detail) {
          errorMessage = `TTS service failed: ${errorJson.detail}`;
        }
      } catch (e) {
        // Keep original error message if JSON parsing fails
      }
      
      return NextResponse.json(
        { error: errorMessage },
        { status: backendResponse.status }
      );
    }

    // Get the audio data from backend
    const audioBuffer = await backendResponse.arrayBuffer();
    console.log('🔊 TTS API: Audio buffer size:', audioBuffer.byteLength);

    // Determine correct Content-Type based on encoding
    const getContentType = (encoding: string): string => {
      switch (encoding) {
        case 'mp3':
          return 'audio/mpeg';
        case 'wav':
          return 'audio/wav';
        case 'linear16':
          return 'audio/wav'; // linear16 is typically served as wav
        default:
          return 'audio/mpeg'; // default fallback
      }
    };

    const contentType = getContentType(encoding);
    console.log('🔊 TTS API: Using Content-Type:', contentType);

    // Return the audio data with proper headers
    return new NextResponse(audioBuffer, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Length': audioBuffer.byteLength.toString(),
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'X-Audio-Encoding': encoding,
        'X-Audio-Voice': voice,
      },
    });

  } catch (error) {
    console.error('🔊 TTS API: Unexpected error:', error);
    console.error('🔊 TTS API: Error stack:', error instanceof Error ? error.stack : 'No stack trace');
    
    // In development, return detailed error information
    const isDevelopment = process.env.NODE_ENV === 'development';
    const errorMessage = isDevelopment && error instanceof Error 
      ? `Internal server error: ${error.message}` 
      : 'Internal server error';
    
    return NextResponse.json(
      { 
        error: errorMessage,
        ...(isDevelopment && { stack: error instanceof Error ? error.stack : undefined })
      },
      { status: 500 }
    );
  }
}

// Handle OPTIONS requests for CORS
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
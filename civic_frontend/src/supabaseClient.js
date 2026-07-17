import { createClient } from '@supabase/supabase-js'

const supabaseUrl =
  import.meta.env.VITE_SUPABASE_URL || 'https://actiazzoahwgjawamrca.supabase.co'
const supabaseAnonKey =
  import.meta.env.VITE_SUPABASE_ANON_KEY ||
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjdGlhenpvYWh3Z2phd2FtcmNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMDU5ODAsImV4cCI6MjA3Mzg4MTk4MH0.HTVLEIT-7N29owbWTjbU7NmccmMBLtgXR0ngeKAIZRs'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

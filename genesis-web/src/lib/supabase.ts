import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || "";

// Safe initialization
export const supabase = (supabaseUrl && supabaseKey)
    ? createClient(supabaseUrl, supabaseKey)
    : {
        from: () => ({ select: () => ({ data: [], error: null }), order: () => ({ data: [], error: null }), insert: () => ({ error: null }) }),
        channel: () => ({ on: () => ({ on: () => ({ subscribe: () => { } }) }), subscribe: () => { } }),
        removeChannel: () => { }
    } as any;

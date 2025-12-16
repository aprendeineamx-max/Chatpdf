
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || "";

// Robust Mock Builder (Thenable)
const createMockBuilder = (data: any[] = []) => {
    return {
        // Thenable interface to work with 'await'
        then(onFulfilled: any, onRejected: any) {
            return Promise.resolve({ data, error: null }).then(onFulfilled, onRejected);
        },

        // Chainable methods
        select: function () { return this; },
        order: function () { return this; },
        eq: function () { return this; },
        limit: function () { return this; },
        single: function () {
            // Return single item or null if empty
            const singleData = data.length > 0 ? data[0] : null;
            return {
                then(onFulfilled: any, onRejected: any) {
                    return Promise.resolve({ data: singleData, error: null }).then(onFulfilled, onRejected);
                }
            };
        },
        insert: function () { return Promise.resolve({ data: [], error: null }); }
    };
};

const mockClient = {
    from: () => createMockBuilder([]),
    channel: () => ({
        on: () => ({
            on: () => ({
                subscribe: () => { }
            }),
            subscribe: () => { }
        }),
        subscribe: () => { }
    }),
    removeChannel: () => { }
};

// Safe initialization
export const supabase = (supabaseUrl && supabaseKey)
    ? createClient(supabaseUrl, supabaseKey)
    : mockClient as any;

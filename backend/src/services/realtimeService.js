import supabase from '../utils/supabaseClient.js'

/**
 * Subscribe to Supabase Realtime for new review cases and notify admins via Socket.io.
 * @param {import('socket.io').Server} io
 */
export function startReviewCaseRealtime(io) {
  const channel = supabase
    .channel('verification-requests-review')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'verification_requests',
        filter: 'status=eq.review',
      },
      async (payload) => {
        try {
          const request = payload.new
          if (!request || request.status !== 'review') return

          const { data: agent } = await supabase
            .from('agents')
            .select('agent_id, full_name, national_id')
            .eq('agent_id', request.agent_id)
            .maybeSingle()

          io.emit('new_review_case', {
            requestId: request.request_id,
            agentId: request.agent_id,
            agentName: agent?.full_name || 'Unknown agent',
            nationalId: agent?.national_id || null,
            createdAt: request.created_at,
            status: request.status,
          })
        } catch (err) {
          console.error('realtimeService notification error:', err.message)
        }
      }
    )
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'verification_requests',
        filter: 'status=eq.review',
      },
      async (payload) => {
        try {
          const request = payload.new
          const previous = payload.old
          if (!request || request.status !== 'review') return
          if (previous?.status === 'review') return

          const { data: agent } = await supabase
            .from('agents')
            .select('agent_id, full_name, national_id')
            .eq('agent_id', request.agent_id)
            .maybeSingle()

          io.emit('new_review_case', {
            requestId: request.request_id,
            agentId: request.agent_id,
            agentName: agent?.full_name || 'Unknown agent',
            nationalId: agent?.national_id || null,
            createdAt: request.created_at,
            status: request.status,
          })
        } catch (err) {
          console.error('realtimeService update notification error:', err.message)
        }
      }
    )
    .subscribe((status) => {
      console.log(`Supabase realtime (review cases): ${status}`)
    })

  return channel
}

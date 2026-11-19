<template>
  <div class="pending-page">
    <div class="pending-card">
      <span class="entry-symbol" aria-hidden="true"><Clock3 :size="24" /></span>
      <h1>Registration received</h1>
      <p>
        Your account is ready. Your identity verification is pending.
      </p>
      <p class="note">
        We’ll notify you when your result is available. You can also sign in to check your status.
      </p>
      <router-link to="/login" class="btn">Go to sign in</router-link>
    </div>
  </div>
</template>

<script setup>
import { Clock3 } from '@lucide/vue'
</script>

<style scoped>
h1 {
  font-size: 1.5rem;
  color: var(--ink);
  margin-bottom: 1rem;
}

p {
  color: var(--ink);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.note {
  font-size: 0.875rem;
  color: var(--muted);
}

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background: var(--action);
  color: var(--on-brand);
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn:hover {
  background: var(--action-hover);
}
</style>

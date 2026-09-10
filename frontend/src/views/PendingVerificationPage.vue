<template>
  <div class="pending-page">
    <div class="pending-card">
      <div class="icon">✓</div>
      <h1>Registration Received</h1>
      <p>
        Your account has been created successfully. Your identity verification
        process will begin shortly.
      </p>
      <p class="note">
        You will be notified once your verification outcome is available.
        Please sign in to check your status.
      </p>
      <router-link to="/login" class="btn">Go to Sign In</router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.pending-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
}

.pending-card {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1.5rem;
  background: #d4edda;
  color: #155724;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

h1 {
  font-size: 1.5rem;
  color: #16213e;
  margin-bottom: 1rem;
}

p {
  color: #52606d;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.note {
  font-size: 0.875rem;
  color: #9fb3c8;
}

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background: #3e7cb1;
  color: #fff;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn:hover {
  background: #2f6a9b;
}
</style>

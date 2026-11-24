<template>
  <label class="verification-consent">
    <input v-model="accepted" type="checkbox" required />
    <span>I agree to Verity using my registration details, identity document and selfie to verify my identity, including face matching and liveness checks. An administrator may review my submission. Verity keeps uploaded ID and selfie images for 3 business days for pending or verified cases and 5 for manual-review or rejected cases. Weekends are excluded.</span>
  </label>
</template>

<script setup>
const accepted = defineModel({ type: Boolean, required: true })
</script>

<style scoped>
.verification-consent {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  margin: 1rem 0;
  color: var(--ink);
  font-size: 0.875rem;
  line-height: 1.45;
}
.verification-consent input {
  flex: none;
  width: 1rem;
  height: 1rem;
  margin: 0.15rem 0 0;
  accent-color: var(--action);
}
</style>

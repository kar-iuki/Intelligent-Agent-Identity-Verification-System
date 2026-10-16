<template>
  <div id="app">
    <WorkspaceShell v-if="$route.meta.role"><router-view /></WorkspaceShell>
    <AuthShell v-else><router-view /></AuthShell>
  </div>
</template>

<script setup>
import WorkspaceShell from './components/WorkspaceShell.vue'
import AuthShell from './components/AuthShell.vue'
</script>

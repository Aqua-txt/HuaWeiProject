<template>
  <div class="publish-wanted-page">
    <WantedFormCard :wanted-id="route.params.id" @cancel="router.back()" @success="handleSuccess" />
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import WantedFormCard from '../components/WantedFormCard.vue'

const route = useRoute()
const router = useRouter()

function handleSuccess() {
  router.push('/wanteds')
}
</script>

<style scoped>
.publish-wanted-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
}
</style>

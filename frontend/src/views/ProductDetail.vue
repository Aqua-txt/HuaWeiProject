<template>
  <ProductDetailPanel :product-id="route.params.id" />
</template>

<script setup>
import { useRoute } from 'vue-router'
import ProductDetailPanel from '../components/ProductDetailPanel.vue'

const route = useRoute()
</script>

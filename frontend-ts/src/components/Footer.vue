<template>
  <v-footer
    id="footer"
    padless
    :class="{
      footer: isAbs,
      'd-flex': true,
      'align-center': true,
      'justify-center': true,
      ' unselectable': true,
    }"
  >
    <div style="font-size: 15px">
      <strong> @SAC Research Lab - Concordia University 2024-2025 </strong>
    </div>
  </v-footer>
</template>

<script setup lang="ts">
defineProps(["isAbs"]);
</script>

<style scoped>
.footer {
  position: absolute;
  bottom: 0;
  right: 0;
  left: 0;
}
</style>

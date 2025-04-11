<template>
  <td class="stt">
    <ExecutionStatusIcon :task_status="task_status"></ExecutionStatusIcon>
  </td>
</template>

<script setup lang="ts">
import ExecutionStatusIcon from "@/components/ExecutionStatusIcon.vue";

const { task_status } = defineProps<{
  task_status: string;
}>();
</script>

<style scoped>
.stt {
  position: relative;
}
.st {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}
</style>

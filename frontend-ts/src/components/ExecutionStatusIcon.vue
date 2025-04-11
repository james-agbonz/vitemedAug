<template>
  <v-tooltip :text="capitalizeFirstLetter(task_status)">
    <template v-slot:activator="{ props }">
      <TransitionGroup name="fade">
        <v-progress-circular
          class="st"
          v-bind="props"
          :size="20"
          color="primary"
          indeterminate
          v-if="task_status === 'running'"
        ></v-progress-circular>
        <v-progress-linear
          v-bind="props"
          v-if="task_status === 'stopping'"
          color="yellow-darken-2"
          indeterminate
        ></v-progress-linear>
        <v-icon
          v-if="task_status === 'finished'"
          v-bind="props"
          class="st"
          icon="mdi-check-bold"
          color="success"
        ></v-icon>
        <v-icon
          v-bind="props"
          class="st"
          v-if="task_status === 'stopped'"
          icon="mdi-stop-circle"
          color="grey"
        ></v-icon>
        <v-icon
          v-bind="props"
          class="st"
          v-if="task_status === 'error'"
          icon="mdi-alert-circle"
          color="error"
        ></v-icon>
        <v-icon
          v-bind="props"
          class="st"
          v-if="task_status === 'initialized'"
          icon="mdi-arrow-right-drop-circle"
          color="blue-grey"
        ></v-icon>
        <v-icon
          v-bind="props"
          class="st"
          v-if="task_status === 'NaN'"
          icon="mdi-circle-off-outline"
          color="blue-grey"
        ></v-icon>
      </TransitionGroup>
    </template>
  </v-tooltip>
</template>

<script setup lang="ts">
import { capitalizeFirstLetter } from "@/plugins/global";

const { task_status } = defineProps<{
  task_status: string;
}>();
</script>

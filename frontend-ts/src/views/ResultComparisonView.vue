<template>
  <v-card style="height: 100%">
    <v-card style="height: 72%; margin-bottom: 3%" elevation="9">
      <v-row class="prov-row">
        <v-col class="pa-0">
          <v-container>
            <v-select
              label="Select Pipeline Execution"
              :items="pipeline_list"
              style="width: 100%"
              variant="solo-filled"
              density="compact"
              item-title="pipeline_execution_name"
              item-value="pipeline_ticket"
              hide-details
            ></v-select>
          </v-container>
        </v-col>
        <!-- <v-divider inset vertical></v-divider> -->
        <v-col class="pa-0">
          <v-container>
            <v-select
              label="Select Pipeline Execution"
              :items="pipeline_list"
              style="width: 100%"
              variant="solo-filled"
              density="compact"
              item-title="pipeline_execution_name"
              item-value="pipeline_ticket"
              hide-details
            ></v-select>
          </v-container>
        </v-col>
      </v-row>
      <v-divider class="mt-3 mb-1"></v-divider>
      <v-row class="prov-row pl-4 mt-1 mb-1"><h4>Training Task</h4></v-row>
      <v-row class="prov-row mt-0">
        <v-col>
          <v-card class="pt-0">123</v-card>
        </v-col>
        <v-col>
          <v-card class="pt-0">123</v-card>
        </v-col>
      </v-row>
      <v-divider class="mt-2 mb-2"></v-divider>
      <v-row class="prov-row pl-4 mt-1 mb-1"><h4>Training Task</h4></v-row>
      <v-row class="prov-row mt-0">
        <v-col>
          <v-card class="pt-0">123</v-card>
        </v-col>
        <v-col>
          <v-card class="pt-0">123</v-card>
        </v-col>
      </v-row>
      <v-divider class="mt-2 mb-2"></v-divider>
    </v-card>
    <v-card class="mx-auto" style="height: 25%" elevation="9"></v-card>
  </v-card>
</template>

<script setup lang="ts">
import ExecutionStatusIcon from "@/components/ExecutionStatusIcon.vue";

import Api from "@/plugins/api";
import { ax } from "@/plugins/axios-helper";
import { toTitleCase } from "@/plugins/global";
import { onMounted, ref } from "vue";
const { post, get } = ax();

const provenance = ref<any>({});
const pipeline_list = ref<any[]>([]);
const pipeline_execution_info = ref<any[]>([]);

const provenanceApi = new Api<any>("/provenance", {
  success(response, target) {
    provenance.value = response.data;
    console.log(provenance.value);
    pipeline_list.value = provenance.value.pipeline_executions;
  },
});

function getProvenance() {
  console.log("get provenance");
  provenanceApi.fetchItemsList();
}

onMounted(() => {
  getProvenance();
});
</script>

<style>
.prov-row {
  width: 100%;
  margin-top: 0.1em;
  margin-left: 0.1em;
}
</style>

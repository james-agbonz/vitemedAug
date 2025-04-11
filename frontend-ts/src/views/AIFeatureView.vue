<template>
  <v-card
    id="feature-view-card"
    class="mx-auto"
    style="height: 100%"
    :elevation="3"
  >
    <div style="margin: 1em; max-height: 400px; text-align: -webkit-center">
      <v-row>
        <v-col style="margin: 0 1em">
          <h4>
            Medical Image Sample (Status:
            <ExecutionStatusIcon :task_status="predictionStatus" />)
          </h4>
          <v-img
            id="targetImage"
            :src="imageUrl"
            style="margin-top: 1em; max-height: 300px"
          />
        </v-col>
        <v-divider vertical></v-divider>
        <v-col cols="2" class="result-col" style="height: 100%">
          <div v-if="predictionResult !== undefined">
            <h4>Prediction</h4>
            <p>Class Index: {{ predictionResult }}</p>
            <br />
            <h4>Top-3 Probabilities</h4>
            <p v-for="i in predictionTop3Result">
              {{ i }}
            </p>
          </div>
          <h4 v-else>No Prediction</h4>
        </v-col>
        <v-divider vertical></v-divider>
        <v-col style="margin: 0 1em; max-height: 400px">
          <div v-if="explanationUrl !== undefined">
            <h4>Explanation</h4>
            <v-img
              :height="expHeight"
              :width="expWidth"
              :src="explanationUrl"
              style="margin-top: 1em; max-height: 300px"
            />
          </div>
          <h4 v-else>No Explanation</h4>
        </v-col>
      </v-row>
    </div>
    <v-divider></v-divider>
    <v-form class="file-upload" v-on:submit="uploadFile">
      <v-file-input
        v-model="files"
        label="Click and select an image"
        clearable
        accept="image/*"
        show-size
        density="compact"
      ></v-file-input>
      <v-row>
        <v-col cols="4">
          <v-select
            label="Model Service*"
            :items="model_service_list"
            item-title="label"
            item-value="value"
            name="model_service_executor_id"
            v-model="model_service_executor_id"
            required
            density="compact"
            autocomplete="off"
            hide-details
          ></v-select>
        </v-col>
        <v-col cols="8">
          <v-select
            label="Model Checkpoints from Task Executions*"
            :items="model_training_execution_list"
            item-title="task_execution_name"
            item-value="task_ticket"
            name="model_training_execution_ticket"
            v-model="model_training_execution_ticket"
            required
            density="compact"
            autocomplete="off"
            hide-details
          ></v-select>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4">
          <v-select
            label="XAI Service*"
            :items="xai_service_list"
            item-title="label"
            item-value="value"
            name="xai_service_executor_id"
            v-model="xai_service_executor_id"
            required
            density="compact"
            autocomplete="off"
            hide-details
          ></v-select>
        </v-col>
        <v-col cols="8">
          <v-select
            label="XAI Function*"
            :items="xai_task_function_list"
            name="xai_function"
            v-model="xai_task_function_key"
            required
            density="compact"
            autocomplete="off"
            hide-details
          ></v-select>
        </v-col>
      </v-row>
      <v-row justify="end">
        <v-col cols="2">
          <v-btn
            class="mr-4"
            width="100px"
            type="submit"
            block
            color="success"
            size="m"
          >
            Submit
          </v-btn>
        </v-col>
        <v-col cols="2">
          <v-btn class="mr-4" block color="error" @click="clear" size="m"
            >Clear</v-btn
          >
        </v-col>
      </v-row>
    </v-form>
    <v-divider></v-divider>
    <div v-if="classLabels.length > 0" style="padding: 1em">
      <h4>
        Class Labels ({{ classLabels.length }} in total): {{ classLabels }}
      </h4>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import defaultImage from "@/assets/image/please_select_a_file.png";
import ExecutionStatusIcon from "@/components/ExecutionStatusIcon.vue";

const files = ref<File[]>([]);
const imageUrl = ref<string>(defaultImage);
const model_service_list = ref<any>([]);
const model_service_executor_id = ref<string>();

const model_training_execution_list = ref<string[]>([]);
const model_training_execution_ticket = ref<string>();

const xai_service_list = ref<any>([]);
const xai_service_executor_id = ref<string>();

const xai_task_function_list = ref<string[]>([]);
const xai_task_function_key = ref<string>();

const predictionResult = ref<any | undefined>(undefined);
const classLabels = ref<string[]>([]);
const predictionTop3Result = ref<string[]>([]);
const predictionStatus = ref<string>("NaN");

const expHeight = ref<number>(0);
const expWidth = ref<number>(0);

const explanationUrl = ref<string | undefined>(undefined);

function createImage(file: File) {
  const reader = new FileReader();
  reader.onload = (e) => {
    if (e.target && e.target.result) {
      imageUrl.value = e.target.result.toString();
    }
  };
  reader.readAsDataURL(file);
}

watch(files, (n: readonly File[], o) => {
  if (n === undefined) {
    imageUrl.value = defaultImage;
  } else if (n instanceof File) {
    createImage(n);
  } else if (n.length > 0) {
    createImage(n[0]);
  }
});

const taskExecutionApi = new Api<any>("/task_execution");
watch(model_service_executor_id, (n, o) => {
  if (n) {
    taskExecutionApi.getRequest(
      {
        executor_id: n,
        task_type: "training",
      },
      {
        success(response, target) {
          model_training_execution_list.value = response.data;
        },
      }
    );
  }
});

const executorTaskFuncKeyApi = new Api<any>("/executor_task_function_key");
watch(xai_service_executor_id, (n, o) => {
  executorTaskFuncKeyApi.getRequest(
    {
      executor_id: n,
    },
    {
      success(response, target) {
        xai_task_function_list.value = response.data.map((xtf: string) =>
          xtf.replace("_xai", "")
        );
      },
    }
  );
});

import { ax, type AxiosResponse } from "@/plugins/axios-helper";
import Api from "@/plugins/api";
const { post, get } = ax();

function uploadFile(e: Event) {
  e.preventDefault();
  if (files.value instanceof File) {
    predictionStatus.value = "running";
    predictionResult.value = undefined;
    predictionTop3Result.value = [];
    explanationUrl.value = undefined;
    expHeight.value = 0;
    expHeight.value = 0;
    post(
      `${import.meta.env.VITE_CENTRAL_URL}/task_publisher/predict_and_explain`,
      {
        image: files.value,
        model_service_executor_id: model_service_executor_id.value,
        model_training_execution_ticket: model_training_execution_ticket.value,
        xai_service_executor_id: xai_service_executor_id.value,
        xai_task_function_key: xai_task_function_key.value + "_xai",
      },
      {
        success(response) {
          predictionStatus.value = "finished";
          predictionResult.value = response.data.prediction.prediction;
          predictionTop3Result.value = Array.from<number>(
            response.data.prediction.prediction_softmax.keys()
          )
            .sort(
              (a, b) =>
                response.data.prediction.prediction_softmax[b] -
                response.data.prediction.prediction_softmax[a]
            )
            .slice(0, 3)
            .map(
              (idx) =>
                "Class Index " +
                idx +
                ": " +
                (
                  response.data.prediction.prediction_softmax[idx] * 100
                ).toFixed(2) +
                "%"
            );
          explanationUrl.value =
            response.data.explanation_url + "?time=" + Date.now();
          classLabels.value = response.data.prediction.class_labels;
          const targetImageEl = document.getElementById("targetImage");
          expHeight.value = targetImageEl!.clientHeight;
          expWidth.value = targetImageEl!.clientWidth;
          console.log(response.data.prediction);
        },
        error(error) {
          predictionStatus.value = "error";
        },
      }
    );
  }
}

function clear(event: Event) {
  predictionStatus.value = "NaN";
  imageUrl.value = defaultImage;
  model_service_executor_id.value = undefined;
  model_training_execution_ticket.value = undefined;
  xai_service_executor_id.value = undefined;
  xai_task_function_key.value = undefined;
  predictionResult.value = undefined;
  predictionTop3Result.value = [];
  explanationUrl.value = undefined;
  expHeight.value = 0;
  expHeight.value = 0;
  files.value = [];
}

const executorApi = new Api<any>("/executor");

onMounted(() => {
  executorApi.fetchItemListExeConfig = {
    success(response, _) {
      for (const item of response.data) {
        const displayI = {
          label: item.executor_name,
          value: item.executor_id,
        };
        if (item.executor_type === "xai") {
          xai_service_list.value.push(displayI);
        }
        if (item.executor_type === "model") {
          model_service_list.value.push(displayI);
        }
      }
    },
  };
  executorApi.fetchItemsList();
});
</script>

<style scoped>
.file-upload {
  margin: 2em 1em 1em;
}
</style>

<style>
#feature-view-card .st::before {
  height: 30px;
}
</style>

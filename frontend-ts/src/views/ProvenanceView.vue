<template>
  <v-card
    class="mx-auto"
    style="height: 100%; height: 100%; display: flex; flex-direction: column"
    :elevation="3"
  >
    <v-card-title style="position: absolute; padding-left: 2em">
      Provenance Network
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text style="height: 93%; padding: 0">
      <v-container id="graphbox"> </v-container>
      <v-container
        id="nodebox"
        v-if="activeNode !== undefined && activeNode.combo !== undefined"
      >
        <!-- meter panel -->
        <v-expansion-panels
          elevation="12"
          v-if="
            activeNode !== undefined &&
            activeNode.combo !== undefined &&
            count()
          "
          v-model="panel1"
          style="opacity: 1"
        >
          <v-expansion-panel
            style="border-radius: 0.8em; border: 5px solid #ababab"
            value="true"
          >
            <v-expansion-panel-title
              style="min-height: 48px !important; font-weight: 900"
            >
              <!-- {{
                activeNode.data.node_type === "pipeline_sheet"
                  ? "Pipeline"
                  : "Task"
              }} -->
              Accumulated Meters from All Executions
            </v-expansion-panel-title>
            <v-divider></v-divider>
            <v-expansion-panel-text>
              <v-table density="compact" style="max-height: 280px">
                <thead>
                  <tr>
                    <th style="width: 210px !important"></th>
                    <th>Total</th>
                    <th>Average Per Execution</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="key in Object.keys(executionMeters)" :key="key">
                    <td>{{ mapMeterLabel[key] }}</td>
                    <td>
                      {{ meterFormat(key, executionMeters[key] as any, false) }}
                    </td>
                    <td>
                      {{ meterFormat(key, executionMeters[key] as any, true) }}
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <!-- detail panel -->
        <v-expansion-panels class="mt-4" elevation="12" v-model="panel2">
          <v-expansion-panel
            style="border-radius: 0.8em; border: 5px solid #ababab"
            value="true"
          >
            <v-expansion-panel-title
              style="min-height: 48px !important; font-weight: 900"
            >
              {{
                toTitleCase(activeNode.combo).replace(
                  "Training Pipeline",
                  "TME Pipeline"
                )
              }}
              Details
              <v-btn
                v-if="
                  activeNode !== undefined &&
                  activeNode.combo !== undefined &&
                  count()
                "
                elevation="4"
                class="text-none"
                style="margin-left: 1.5em"
                color="success"
                density="compact"
                @click.stop="reproduce"
                >Reproduce</v-btn
              >
            </v-expansion-panel-title>
            <v-divider></v-divider>
            <v-expansion-panel-text style="max-height: 200px">
              <v-table density="compact" style="max-height: 180px">
                <tbody>
                  <tr
                    v-for="([name, value], index) in Object.entries(
                      activeNode.data
                    )"
                    :key="index"
                  >
                    <td style="width: 210px !important">
                      {{ toTitleCase(name) }}
                    </td>
                    <td>{{ value }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-container>
      <div style="position: absolute; top: 4em; left: 1.5em; opacity: 1">
        <div
          class="clearfix"
          v-for="ent in Object.entries(colorMapCombo)"
          :key="ent[0]"
          style="margin-bottom: 4px"
        >
          <div
            style="height: 15px; width: 15px; border-radius: 3px; float: left"
            :style="{
              backgroundColor:ent[1] as string,
            }"
          ></div>
          <div
            style="
              height: 15px;
              line-height: 15px;
              float: left;
              padding-left: 0.7em;
              font-weight: 900;
            "
          >
            {{
              ent[0] === "executor" ? "General AI Service" : toTitleCase(ent[0])
            }}
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import {
  Graph,
  register,
  ExtensionCategory,
  type GraphData,
  AntVDagreLayout,
  ForceAtlas2Layout,
  RandomLayout,
  ConcentricLayout,
  DagreLayout,
  GridLayout,
} from "@antv/g6";
import {
  provenance_cluster_keys,
  mapping,
  ClickNode,
  BreathingCircle,
} from "@/plugins/provenance-g6-helper";
import { onMounted, onUnmounted, ref, watch } from "vue";

import { formatSeconds } from "@/plugins/global";

const provenance = ref<any>({});
const graph = ref<Graph | undefined>(undefined);
const activeNode = ref<any>(undefined);
const executionMeters = ref<any>({});
const panel1 = ref<string>("true");
const panel2 = ref<string>("true");

var resizeTimeoutIntv: number | undefined = undefined;

import Api from "@/plugins/api";
import { toTitleCase } from "@/plugins/global";
import type { ComponentTemplate } from "@/class/ComponentTemplate";

const colorMapCombo: any = {
  executor: "#0cb2af",
  configuration: "#a1c65d",
  task_sheet: "#fac723",
  task_execution: "#f29222",
  pipeline_sheet: "#e95e50",
  pipeline_execution: "#936fac",
};

const mapMeterLabel: any = {
  task_execution_count: "Task Number",
  pipeline_execution_count: "Pipeline Number",
  duration: "Duration",
  emissions: "CO₂ Emissions (kg)",
  energy_consumed: "Energy Consumed (kWh)",
};

function meterFormat(name: string, value: number, perExe: boolean) {
  const durationTimes = 821.7;
  const count =
    activeNode.value.data.node_type === "pipeline_sheet"
      ? executionMeters.value["pipeline_execution_count"]
      : executionMeters.value["task_execution_count"];

  var value = ["task_execution_count", "pipeline_execution_count"].includes(
    name
  )
    ? value
    : value * durationTimes;

  if (perExe) {
    if (name === "task_execution_count") return "-";
    if (name === "pipeline_execution_count") return "-";
    if (name === "emissions")
      return ((value as number) / count).toExponential(2);
    if (name === "energy_consumed")
      return ((value as number) / count).toExponential(2);
    if (name === "duration")
      return `${formatSeconds(Math.round(value / count))}`;
  } else {
    if (name === "duration") return `${formatSeconds(Math.round(value))}`;
    if (name === "emissions") return value.toExponential(2);
    if (name === "energy_consumed") return value.toExponential(2);
  }
  return value;
}

function renderGraph() {
  let data: GraphData = provenance.value;
  console.log(data);
  const g = new Graph({
    container: "graphbox",
    autoFit: "view",
    data,
    node: {
      // type: "rect",
      style: {
        size: 200,
        labelText: (d) => `${d.label}`,
        // https://g.antv.antgroup.com/api/basic/text#fontweight
        labelFontWeight: "bold",
        labelPlacement: "center",
        labelFontSize: 40,
        labelWordWrap: true,
        labelWordWrapWidth: 120,
        labelMaxLines: 3,
        labelLeading: 30,
        labelTextAlign: "center",
        opacity: 1.0,
        // ports: [{ placement: "left" }, { placement: "right" }],
        ports: [{ placement: "top" }, { placement: "bottom" }],
      },
      state: {
        "r-select": {
          halo: true,
        },
        "r-not-select": {
          opacity: 0.2,
          fill: "rgba(135, 135, 135, 0.31)",
        },
        "c-select": {
          halo: true,
          haloLineWidth: 170,
        },
      },
      palette: {
        type: "group",
        field: "node_type",
      },
    },
    edge: {
      type: "cubic-vertical",
      style: {
        endArrow: true,
        endArrowSize: 30,
        endArrowLineWidth: 10,
        labelText: undefined,
        labelFontSize: 120,
        labelFontWeight: "bold",
        // labelDy: 30,
        labelBackground: true,
        labelPadding: 30,
        labelOpacity: 1,
        labelFill: "red",
        // labelBackgroundFill: "grey",
        labelBackgroundOpacity: 0.7,
        labelBackgroundRadius: 30,
        lineWidth: 5,
        opacity: 0.5,
        zIndex: -1,
        // fill: "white",
        fillOpacity: 0,
      },
      state: {
        "r-select": {
          halo: true,
          haloFillOpacity: 0.6,
          opacity: 1,
          labelText: (d) => {
            let label = d.label as string;
            // return label.toUpperCase();
            return label;
          },
          // fill: "rgba(135, 135, 135, 0.31)",
          // zIndex: 10,
        },
        "r-not-select": {
          lineWidth: 1,
          opacity: 0.2,
        },
      },
    },
    combo: {
      type: "rect",
      style: {
        labelText: (d) =>
          `${toTitleCase(d.id)
            .replace("Xai", "XAI")
            .replace("Training Pipeline", "TME Pipeline")
            .replace("Executor", "Service")}`,
        labelFontWeight: "bolder",
        labelFontSize: 200,
        labelBackground: true,
        labelFill: "white",
        labelBackgroundFill: "black",
        labelPadding: 40,
        labelOpacity: 1,
        labelDy: 40,
        labelWordWrap: true,
        labelWordWrapWidth: 1800,
        labelBackgroundRadius: 30,
        labelMaxLines: 2,
        labelLeading: 10,
        labelTextAlign: "center",
        // lineDash: 0,
        // collapsedLineDash: [5, 5],
        padding: 50,
        radius: 120,
        lineWidth: 5,
        // zIndex: 100,
        opacity: 1,
      },
      state: {
        "r-select": {
          lineWidth: 7,
          halo: true,
        },
        "r-not-select": {
          lineWidth: 1,
          opacity: 0.2,
        },
      },
    },
    layout: {
      type: "combo-combined",
      nodeSize: (node: any) => {
        return 500;
      },
      outerLayout: new AntVDagreLayout({
        // sortByCombo: true,
        rankdir: "LR",
        ranker: "tight-tree",
        nodesep: 220,
        ranksep: 700,
      }),
      groupByTypes: true,
      preventOverlap: true,
      spacing: 20,
    },
    behaviors: [
      "drag-canvas",
      "zoom-canvas",
      // "drag-element",

      {
        type: "my-click-node",
        activeNode: activeNode,
        executionMeters: executionMeters,
      },
    ],
    padding: 30,
    animation: false,
    // animation: true,
    plugins: [
      {
        type: "toolbar",
        position: "left-top",
        onClick: (item: any) => {
          // window.dispatchEvent(new Event("resize"));
          resizeHandler();
        },
        getItems: () => {
          return [{ id: "reset", value: "reset" }];
        },
      },
    ],
  });
  g.render();
  graph.value = g;
}

function reRenderGraph() {
  if (graph.value === undefined) {
    renderGraph();
  } else {
    graph.value
      .clear()
      .then((e) => graph.value!.destroy())
      .then((e) => renderGraph());
  }
}

const provenanceApi = new Api<any>("/provenance", {
  success(response, target) {
    provenance.value = response.data;
    reRenderGraph();
    register(
      ExtensionCategory.BEHAVIOR,
      "my-click-node",
      ClickNode,
      // override registration
      true
    );
    register(ExtensionCategory.NODE, "breathing-circle", BreathingCircle);
  },
});

function getProvenance() {
  console.log("get provenance");
  provenanceApi.fetchItemsList();
}

function resizeHandler() {
  clearTimeout(resizeTimeoutIntv);
  resizeTimeoutIntv = setTimeout(() => {
    let container = document.getElementById("graphbox");
    let width = container!.getBoundingClientRect().width;
    let height = container!.getBoundingClientRect().height;
    graph.value!.resize(width, height);
    // @ts-expect-error
    graph.value!.autoFit();
  }, 100);
}

const taskSheetApi = new Api<ComponentTemplate>("/task_sheet");
const pipelineSheetApi = new Api<ComponentTemplate>("/pipeline_sheet");

function reproduce() {
  if (activeNode.value.combo.endsWith("pipeline sheet")) {
    pipelineSheetApi.postRequest(
      {
        act: "execute",
        ...activeNode.value.data,
      },
      {
        success(response, target) {
          getProvenance();
        },
      }
    );
  } else {
    taskSheetApi.postRequest(
      {
        act: "execute",
        task_sheet_id: activeNode.value.id,
      },
      {
        success(response, target) {
          getProvenance();
        },
      }
    );
  }
}

function count() {
  return (
    activeNode.value.combo.endsWith("task sheet") ||
    activeNode.value.combo.endsWith("pipeline sheet")
  );
}

const resizeObserver = new ResizeObserver((elmList) => {
  for (let e of elmList) {
    resizeHandler();
  }
});

onMounted(() => {
  getProvenance();
  resizeObserver.observe(document.getElementById("mainPanel")!);
});
onUnmounted(() => {
  resizeObserver.unobserve(document.getElementById("mainPanel")!);
});
</script>

<style>
.fade-enter-active {
  transition: all 0.2s;
}
.fade-leave-active {
  transition: all 0.2s ease-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
#graphbox {
  height: 100%;
  width: 100%;
  float: left;
  padding: 0em;
  /* border: 2px #b0b0b0 solid;
  border-radius: 1em; */
  transition: width 0.5s ease, height 0.5s ease; /* Smooth transition for width and height */
}
#nodebox {
  width: 600px;
  /* border: 1px rgb(191, 191, 191) solid; */
  overflow-y: auto;
  border-radius: 1em;
  position: absolute;
  right: 2em;
  top: 1em;
  /* padding: 0; */
}

#nodeHead {
  background-color: #a6a4a426;
}

#controls {
  position: absolute;
  right: 1em;
  top: 76px;
  background-color: white;
}
#search {
  position: absolute;
  right: 1em;
  top: 120px;
  width: 300px;
  background-color: white;
  border: 1px #00000026 solid;
  padding: 6px 6px 10px 6px;
  border-radius: 10px;
}
#legend {
  position: absolute;
  left: 1em;
  bottom: 14px;
  background-color: white;
  border: 1px #00000026 solid;
  padding: 6px;
  border-radius: 10px;
  opacity: 0.5;
}

.legendTitle {
  float: right;
  height: 21.73px;
  line-height: 21.73px;
  margin-left: 5px;
  width: 220px;
}

/* 对于 WebKit 和 Blink 浏览器（如 Chrome, Safari） */
::-webkit-scrollbar {
  width: 8px; /* 滚动条的宽度 */
}

::-webkit-scrollbar-track {
  background: transparent; /* 隐藏轨道，设置为透明 */
}

::-webkit-scrollbar-thumb {
  background: #888; /* 滚动条的颜色 */
  border-radius: 20px; /* 滚动条的圆角 */
}

::-webkit-scrollbar-thumb:hover {
  background: #555; /* 滚动条悬停时的颜色 */
}
</style>

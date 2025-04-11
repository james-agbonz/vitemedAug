import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "Service",
      component: () => import("@/views/ServiceView.vue"),
    },
    {
      path: "/configuration",
      name: "Configuration",
      component: () => import("@/views/ConfigurationView.vue"),
    },
    {
      path: "/task_sheet",
      name: "TaskSheet",
      component: () => import("@/views/TaskSheetView.vue"),
    },
    {
      path: "/pipeline_sheet",
      name: "Pipeline Sheet",
      component: () => import("@/views/PipelineSheetView.vue"),
    },
    {
      path: "/predict_and_explain",
      name: "Predict & Explain",
      component: () => import("@/views/AIFeatureView.vue"),
    },
    {
      path: "/provenance",
      name: "Provenance",
      component: () => import("@/views/ProvenanceView.vue"),
    },
    {
      path: "/emission_meters",
      name: "Emission Meters",
      component: () => import("@/views/EmissionMeterView.vue"),
    },
    {
      path: "/rs_compare",
      name: "Result Comparison",
      component: () => import("@/views/ResultComparisonView.vue"),
    },
  ],
});

export default router;

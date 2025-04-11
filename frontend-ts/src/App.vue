<template>
  <v-app id="app">
    <!-- <v-navigation-drawer>...</v-navigation-drawer> -->
    <v-app-bar :elevation="6" color="#00796B">
      <v-app-bar-title style="font-weight: bold"
        >Machine Learning and XAI Ops for Medical Image Classification
        (MLXOps4Medic)</v-app-bar-title
      >
    </v-app-bar>
    <v-main>
      <v-navigation-drawer
        id="nav_"
        permanent
        location="left"
        :elevation="4"
        :rail="rail"
        @click="rail = false"
        width="200"
      >
        <!-- <template v-slot:prepend> -->
        <v-list-item
          lines="two"
          prepend-avatar="https://randomuser.me/api/portraits/lego/8.jpg"
          title="Test User"
          subtitle="Logged in"
          nav
        >
          <template v-slot:append>
            <v-btn
              variant="text"
              icon="mdi-chevron-left"
              @click.stop="rail = !rail"
            ></v-btn>
          </template>
        </v-list-item>
        <!-- </template> -->

        <v-divider></v-divider>

        <v-list density="compact" nav>
          <v-list-subheader style="font-weight: bold"
            >-- DevOps Workflows --</v-list-subheader
          >
          <v-list-item
            v-for="tab in devTabs"
            :key="tab.title"
            :prepend-icon="tab.icon"
            :title="tab.title"
            @click="clickTab(tab.title)"
            :active="checkIsCurrentTab(tab.title)"
            class="unselectable"
            elevation="3"
            variant="outlined"
          ></v-list-item>
        </v-list>
        <v-divider></v-divider>

        <v-list density="compact" nav>
          <v-list-subheader style="font-weight: bold"
            >-- MLX Workflows --</v-list-subheader
          >
          <v-list-item
            v-for="tab in mlTabs"
            :key="tab.title"
            :prepend-icon="tab.icon"
            :title="tab.title"
            @click="clickTab(tab.title)"
            :active="checkIsCurrentTab(tab.title)"
            class="unselectable"
            elevation="3"
            variant="outlined"
          ></v-list-item>
        </v-list>
      </v-navigation-drawer>

      <div
        id="mainPanel"
        class="mainPanel"
        :style="{
          height: mainHeight,
        }"
      >
        <router-view v-slot="{ Component }" :elevation="10">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        <Footer style="margin-top: 0.5em" :isAbs="false"></Footer>
      </div>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import Footer from "@/components/Footer.vue";
import router from "@/router";
import { computed, onMounted, ref } from "vue";

let rail = ref(true);
let currentTab = ref("");

const mlTabs = [
  {
    icon: "mdi-file-table-outline",
    title: "Task Sheet",
    path: "/task_sheet",
  },
  {
    icon: "mdi-pipe",
    title: "Pipeline Sheet",
    path: "/pipeline_sheet",
  },
  {
    icon: "mdi-telescope",
    title: "Predict & Explain",
    path: "/predict_and_explain",
  },
];

const devTabs = [
  {
    icon: "mdi-server",
    title: "Service",
    path: "/",
  },
  {
    icon: "mdi-cog",
    title: "Configuration",
    path: "/configuration",
  },
  {
    icon: "mdi-graphql",
    title: "Provenance",
    path: "/provenance",
  },
  // {
  //   icon: "mdi-compare-vertical",
  //   title: "Result Comparison",
  //   path: "/rs_compare",
  // },
  {
    icon: "mdi-chart-bar-stacked",
    title: "Emission Meter",
    path: "/emission_meters",
  },
];
const tabList = [...mlTabs, ...devTabs];

function findPathByTab(tab: string) {
  let target = undefined;
  for (const tabItem of tabList) {
    if (tabItem.title === tab) {
      target = tabItem;
    }
  }
  return target;
}
function clickTab(tab: string) {
  currentTab.value = tab;
  let tabItem = findPathByTab(tab);
  if (tabItem !== undefined) router.push(`${tabItem.path}`);
}
function checkIsCurrentTab(targetTab: string) {
  return targetTab === currentTab.value;
}

const mainHeight = ref<string>(window.innerHeight - 64 + "px");

function resizeMain() {
  mainHeight.value = window.innerHeight - 64 + "px";
}

onMounted(() => {
  let sp = window.location.href.split("/");
  let path = "/" + sp[sp.length - 1];
  let tab = "";
  for (const i of tabList) {
    if (path === i.path) {
      tab = i.title;
    }
  }
  clickTab(tab);
  window.removeEventListener("resize", resizeMain, false);
  window.addEventListener("resize", resizeMain, true);
});
</script>

<style scoped>
.mainPanel {
  padding: 1.2em 1.2em 3em 1.2em;
}

.view {
  height: 100%;
  /* position: absolute; */
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
  /* right: -10%; */
  transform: translateX(-10px);
  opacity: 0;
}

.slide-r-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-r-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-r-fade-enter, .slide-r-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
  /* right: -10%; */
  transform: translateX(10px);
  opacity: 0;
}

.small-slide-r-fade-enter-active {
  transition: all 0.3s ease;
}
.small-slide-r-fade-leave-active {
  transition: all 0.3s ease;
}
.small-slide-r-fade-enter, .small-slide-r-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
  /* right: -10%; */
  transform: translateX(3px);
  opacity: 0;
}
</style>

<style>
@import "@/assets/css/index.less";
.trHover {
  transition: all 0.5s !important;
  cursor: pointer;
}
.trHover:hover {
  background-color: rgba(219, 219, 219, 0.627);
}
.v-list-item__spacer {
  width: 10px !important;
}
</style>

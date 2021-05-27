<template>
  <div>
    <div class="row">
      <div class="col col-8 export-table-modal__actions"></div>
      <div class="col col-4 export-table-modal__actions">
        <button
          v-if="job.status === 'complete'"
          class="button button--large button--primary export-table-modal__export-button"
          :class="{ 'button--loading': loading }"
          :disabled="loading"
        >
          Re-Export
        </button>
      </div>
    </div>
    <div class="row">
      <div class="col col-8 export-table-modal__actions">
        <div v-if="job !== null" class="export-table-modal__loading-bar">
          <div
            class="export-table-modal__loading-bar-inner"
            :style="{
              width: `${job.progress_percentage * 100}%`,
              'transition-duration': [1, 0].includes(job.progress_percentage)
                ? '0s'
                : '1s',
            }"
          ></div>
          <span v-if="jobIsRunning" class="export-table-modal__status-text">
            {{ job.status }}
          </span>
        </div>
      </div>
      <div class="col col-4 align-right export-table-modal__actions">
        <button
          v-if="job === null"
          class="button button--large button--primary export-table-modal__export-button"
          :class="{ 'button--loading': loading }"
          :disabled="loading"
        >
          Export
        </button>
        <button
          v-else-if="jobIsRunning"
          class="button button--large button--primary button--loading export-table-modal__export-button"
          :disabled="loading"
        ></button>
        <a
          v-else-if="job.status === 'complete'"
          class="button button--large button--success export-table-modal__export-button"
          :href="job.url"
          target="_blank"
        >
          Download
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExportTableLoadingBar',
  props: {
    job: {
      type: Object,
      required: false,
      default: null,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    jobIsRunning() {
      return (
        this.job !== null && ['exporting', 'pending'].includes(this.job.status)
      )
    },
  },
}
</script>

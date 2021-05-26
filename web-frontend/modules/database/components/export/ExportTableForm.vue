<template>
  <div>
    <Error :error="error"></Error>
    <form @submit.prevent="exportViewOrTable">
      <div class="row">
        <div class="col col-12">
          <div class="control">
            <label class="control__label">Select the view to export:</label>
            <div class="control__elements">
              <ExportTableDropdown
                v-model="selectedView"
                :loading="loading"
                :table="table"
              ></ExportTableDropdown>
            </div>
          </div>
          <div v-if="exporterTypes.length > 0" class="control">
            <label class="control__label"
              >To which format would you like to export?</label
            >
            <div class="control__elements">
              <ul class="choice-items">
                <li
                  v-for="exporterType in exporterTypes"
                  :key="exporterType.type"
                >
                  <a
                    class="choice-items__link"
                    :class="{
                      active: exporter.type === exporterType.type,
                      disabled: loading,
                    }"
                    @click="switchToExporterType(exporterType)"
                  >
                    <i
                      class="choice-items__icon fas"
                      :class="'fa-' + exporterType.iconClass"
                    ></i>
                    {{ exporterType.name }}
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <component
        :is="exporterComponent"
        v-model="exporterOptions"
        :loading="loading"
      />
      <div class="row">
        <div class="col col-8 export-table-modal__actions">
          <div v-if="job !== null" class="export-table-modal__loading-bar">
            <div
              class="export-table-modal__loading-bar-inner"
              :style="{
                width: `${job.progress_percentage * 100}%`,
                'transition-duration':
                  job.progress_percentage === 1 ? '0s' : '1s',
              }"
            ></div>
          </div>
        </div>
        <div class="col col-4 align-right export-table-modal__actions">
          <button
            v-if="job === null"
            class="button button--large button--primary export-table-modal__export-button"
            :class="{ 'button--loading': loading }"
            :disabled="loading || exporter === null"
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
    </form>
  </div>
</template>

<script>
import error from '@baserow/modules/core/mixins/error'
import ExportTableDropdown from '@baserow/modules/database/components/export/ExportTableDropdown'
import ExporterService from '@baserow/modules/database/services/export'

export default {
  name: 'ExportTableForm',
  components: { ExportTableDropdown },
  mixins: [error],
  props: {
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      loading: false,
      exporter: null,
      exporterOptions: {},
      job: null,
      pollInterval: null,
      selectedView: this.view,
    }
  },
  computed: {
    exporterTypes() {
      return this.getExporterTypes(this.selectedView)
    },
    exporterComponent() {
      return this.exporter === null ? null : this.exporter.getFormComponent()
    },
    jobIsRunning() {
      return (
        this.job !== null && ['exporting', 'pending'].includes(this.job.status)
      )
    },
  },
  watch: {
    selectedView() {
      this.switchToFirstAvailableExporterType()
    },
  },
  created() {
    this.switchToFirstAvailableExporterType()
  },
  destroyed() {
    clearInterval(this.pollInterval)
  },
  methods: {
    switchToFirstAvailableExporterType() {
      const startingExporterType =
        this.exporterTypes.length > 0 ? this.exporterTypes[0] : null

      // If there is a currently selected export type and the new view / table also
      // supports that type then keep it selected.
      if (
        this.exporter !== null &&
        this.exporterTypes.find((t) => t.type === this.exporter.type) !==
          undefined
      ) {
        return
      }
      this.switchToExporterType(startingExporterType)
    },
    switchToExporterType(exporterType) {
      if (this.loading) {
        return
      }

      this.hideError()
      this.exporter = exporterType
      if (this.exporterTypes.length === 0) {
        this.showError(
          'No supported exporters found',
          'Please switch to another view or table.'
        )
      }
    },
    getExporterTypes(view) {
      const types = Object.values(this.$registry.getAll('exporter'))
      return types.filter((exporterType) => {
        if (view !== null) {
          return exporterType.getSupportedViews().includes(view.type)
        } else {
          return exporterType.getCanExportTable()
        }
      })
    },
    async getLatestJobInfo() {
      try {
        const { data } = await ExporterService(this.$client).get(this.job.id)
        this.job = data
        if (!this.jobIsRunning) {
          clearInterval(this.pollInterval)
        }
        if (this.job.status === 'failed' || this.job.status === 'cancelled') {
          const title =
            this.job.status === 'failed' ? 'Export Failed' : 'Export Cancelled'
          const message =
            this.job.status === 'failed'
              ? 'The export failed due to a server error.'
              : 'The export was cancelled.'
          this.job = null
          this.loading = false
          this.showError(title, message)
        }
      } catch (error) {
        // We could preserve the job and do some sort of exponential polling backoff
        // here as the error might be a transient one. However having all clients
        // instantly stop applying load to the server if a problem occurs seems
        // more prudent and worth loosing potentially recoverable export jobs.
        this.loading = false
        this.job = null
        if (this.pollInterval) {
          clearInterval(this.pollInterval)
        }
        this.handleError(error, 'application')
      }
    },
    async exportViewOrTable() {
      this.loading = true
      this.hideError()

      try {
        const { data } = await ExporterService(this.$client).export(
          this.selectedView === null ? this.table.id : null,
          this.selectedView !== null ? this.selectedView.id : null,
          this.exporter,
          this.exporterOptions
        )
        this.job = data
        if (this.pollInterval !== null) {
          clearInterval(this.pollInterval)
        }
        if (this.jobIsRunning) {
          this.pollInterval = setInterval(this.getLatestJobInfo, 1000)
        } else if (this.job.status !== 'complete') {
          this.loading = false
        }
      } catch (error) {
        this.loading = false
        this.job = null
        if (this.pollInterval) {
          clearInterval(this.pollInterval)
        }
        this.handleError(error, 'application')
      }
    },
  },
}
</script>

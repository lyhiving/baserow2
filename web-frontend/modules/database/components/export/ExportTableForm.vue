<template>
  <div>
    <Error :error="error"></Error>
    <form @submit.prevent="exportViewOrTable">
      <div class="row">
        <div class="col col-12">
          <div class="control">
            <label class="control__label"
              >Select the view or table to export:</label
            >
            <div class="control__elements">
              <ExportTableDropdown
                :table="table"
                :selected-view="view"
              ></ExportTableDropdown>
            </div>
          </div>
          <div class="control">
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
                    :class="{ active: exporter === exporterType.type }"
                    @click="exporter = exporterType.type"
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
      <component :is="exporterComponent" v-model="exporterOptions" />
      <div>
        <p></p>
        <div class="actions">
          <div v-if="job !== null" class="export-table-modal__loading-bar">
            <div
              class="export-table-modal__loading-bar-inner"
              :style="{
                width: `${job.progress_percentage * 100}%`,
              }
            ></div>
          </div>
          <div class="export-table-modal__export-button">
            <button
              v-if="job === null"
              class="button button--large button--primary"
              :class="{ 'button--loading': loading }"
              :disabled="loading"
            >
              Export
            </button>
            <button
              v-else-if="jobIsRunning"
              class="button button--large button--primary button--loading"
              :disabled="loading"
            ></button>
            <a
              v-else-if="job.status === 'completed'"
              class="button button--large button--success"
              :disabled="loading"
              :href="job.url"
            >
              Download
            </a>
          </div>
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
      exporter: '',
      exporterOptions: {},
      job: null,
      pollInterval: null,
    }
  },
  computed: {
    exporterTypes() {
      return Object.values(this.$registry.getAll('exporter')).filter(
        this.exporterTypeSupportsSelectedView
      )
    },
    exporterComponent() {
      return this.exporter === ''
        ? null
        : this.$registry.get('exporter', this.exporter).getFormComponent()
    },
    jobIsRunning() {
      return (
        this.job !== null && ['exporting', 'pending'].includes(this.job.status)
      )
    },
  },
  destroyed() {
    clearInterval(this.pollInterval)
  },
  methods: {
    exporterTypeSupportsSelectedView(exporterType) {
      if (this.view !== null) {
        return exporterType.getSupportedViews().includes(this.view.type)
      } else {
        return exporterType.getCanExportTable()
      }
    },
    async getLatestJobInfo() {
      try {
        const { data } = await ExporterService(this.$client).get(this.job.id)
        this.job = data
        if (!this.jobIsRunning) {
          clearInterval(this.pollInterval)
        }
        if (this.job.status === 'failed') {
          this.job = null
          const handler = {
            handler: {
              getMessage() {
                return {
                  title: 'Export Failed.',
                  message: 'Something went wrong on the server.',
                }
              },
              handled() {},
            },
          }
          this.handleError(handler, 'application')
        }
      } catch (error) {
        console.log(error)
        this.handleError(error, 'application')
      }
    },
    async exportViewOrTable() {
      this.loading = true
      this.hideError()

      try {
        const { data } = await ExporterService(this.$client).export(
          this.view === null ? this.table.id : null,
          this.view !== null ? this.view.id : null,
          this.exporter,
          this.exporterOptions
        )
        this.loading = false
        this.job = data
        if (this.pollInterval !== null) {
          clearInterval(this.pollInterval)
        }
        if (this.jobIsRunning) {
          this.pollInterval = setInterval(this.getLatestJobInfo, 1000)
        }
      } catch (error) {
        this.loading = false
        this.handleError(error, 'application')
      }
    },
  },
}
</script>

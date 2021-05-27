<template>
  <div>
    <Error :error="error"></Error>
    <form @submit.prevent="submitted">
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
          <ExporterTypeChoices
            v-model="exporter"
            :view="selectedView"
            :loading="loading"
          ></ExporterTypeChoices>
        </div>
      </div>
      <component :is="exporterComponent" :loading="loading" />
      <ExportTableLoadingBar
        :job="job"
        :loading="loading || exporter === null"
      ></ExportTableLoadingBar>
    </form>
  </div>
</template>

<script>
import error from '@baserow/modules/core/mixins/error'
import ExportTableDropdown from '@baserow/modules/database/components/export/ExportTableDropdown'
import ExporterService from '@baserow/modules/database/services/export'
import form from '@baserow/modules/core/mixins/form'
import ExporterTypeChoices from '@baserow/modules/database/components/export/ExporterTypeChoices'
import ExportTableLoadingBar from '@baserow/modules/database/components/export/ExportTableLoadingBar'

export default {
  name: 'ExportTableForm',
  components: {
    ExporterTypeChoices,
    ExportTableDropdown,
    ExportTableLoadingBar,
  },
  mixins: [error, form],
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
      job: null,
      pollInterval: null,
      selectedView: this.view,
      values: {},
    }
  },
  computed: {
    exporterComponent() {
      return this.exporter === null ? null : this.exporter.getFormComponent()
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
    async getLatestJobInfo() {
      try {
        const { data } = await ExporterService(this.$client).get(this.job.id)
        this.job = data
        if (!this.jobIsRunning) {
          this.loading = false
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
    async submitted(values) {
      this.loading = true
      this.hideError()

      try {
        const { data } = await ExporterService(this.$client).export(
          this.table.id,
          this.selectedView !== null ? this.selectedView.id : null,
          this.exporter,
          values
        )
        this.job = data
        if (this.pollInterval !== null) {
          clearInterval(this.pollInterval)
        }
        if (this.jobIsRunning) {
          this.pollInterval = setInterval(this.getLatestJobInfo, 1000)
        } else {
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

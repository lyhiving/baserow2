import { PremPlugin } from '@baserow_premium/plugins'
import { UsersAdminType } from '@baserow_premium/adminTypes'
import {
  JSONTableExporter,
  XMLTableExporter,
} from '@baserow_premium/tableExporterTypes'

export default ({ app }) => {
  app.$registry.register('plugin', new PremPlugin())
  app.$registry.register('admin', new UsersAdminType())
  app.$registry.register('exporter', new JSONTableExporter())
  app.$registry.register('exporter', new XMLTableExporter())
}

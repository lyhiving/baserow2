<template>
  <Modal>
    <h2 class="box__title">
      {{ $t('webhookModal.title', { tableName: table.name }) }}
    </h2>
    <Error :error="error"></Error>
    <div class="align-right">
      <a href="#" class="button" @click="toggleCreateForm()">
        <i v-if="!renderList" class="fas fa-arrow-left"></i>
        {{
          renderList
            ? $t('webhookModal.toggleCreateFormButton.createWebhook')
            : $t('webhookModal.toggleCreateFormButton.backToList')
        }}
        <i v-if="renderList" class="fas fa-plus"></i>
      </a>
    </div>
    <webhook-list :table="table" :render-list="renderList" />
    <div v-if="!renderList" class="webhook__list">
      <create-webhook-context :table="table" @created="toggleCreateForm()" />
    </div>
  </Modal>
</template>

<script>
import WebhookList from './WebhookList.vue'
import CreateWebhookContext from './CreateWebhookContext.vue'
import modal from '@baserow/modules/core/mixins/modal'
import error from '@baserow/modules/core/mixins/error'

export default {
  name: 'WebhookModal',
  components: {
    CreateWebhookContext,
    WebhookList,
  },
  mixins: [modal, error],
  props: {
    table: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      renderList: true,
    }
  },
  methods: {
    toggleCreateForm() {
      this.renderList = !this.renderList
    },
  },
}
</script>

<i18n>
{
  "en": {
    "webhookModal": {
      "title": "Webhooks {tableName} table",
      "toggleCreateFormButton": {
        "createWebhook": "Create webhook",
        "backToList": "Back to list"
      }
    }
  },
  "fr": {
    "webhookModal": {
      "title": "@TODO",
      "toggleCreateFormButton": {
        "createWebhook": "@TODO",
        "backToList": "@TODO"
      }
    }
  }
}
</i18n>

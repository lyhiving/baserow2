import {PremPlugin} from '@baserow_premium/plugins'

export default ({app}) => {
    console.log("Hello world from the prem plugin!")

    app.$registry.register('plugin', new PremPlugin())
}

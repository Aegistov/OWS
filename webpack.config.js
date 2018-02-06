var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
    //the base directory for resolving the entry option
    context: __dirname,
    entry: {
        main: './static/js/index',
        ows: './static/js/ows',
    },
    output: {
        path: path.resolve('./static/bundles/'),
        filename: '[name]-[hash].js',
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        })
    ],
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: ['react']
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader','css-loader']
            }
        ]
    },
    resolve: {
        modules: ['node_modules'],
        extensions: ['.js', '.jsx']
    }
}

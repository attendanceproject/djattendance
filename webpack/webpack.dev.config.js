var path = require("path")
var webpack = require('webpack')
var BundleTracker  = require('webpack-bundle-tracker')
var merge = require('webpack-merge')

var commonConfig = require('./webpack.common.config')

var devConfig = {
  mode: 'development',
  entry: {
    main: [
      'webpack-dev-server/client?http://localhost:3000',
      'webpack/hot/only-dev-server',
    ],
    jquery_bootstrap: [
      'webpack-dev-server/client?http://localhost:3000',
      'webpack/hot/only-dev-server',
    ],
    select_2: [
      'webpack-dev-server/client?http://localhost:3000',
      'webpack/hot/only-dev-server',
    ],
    attendance: [
      'react-hot-loader/patch',
      'webpack-dev-server/client?http://localhost:3000',
      'webpack/hot/only-dev-server',
    ],
    tinymce: [
      'webpack-dev-server/client?http://localhost:3000',
      'webpack/hot/only-dev-server',
    ],
  },

  output: {
    publicPath: 'http://localhost:3000/ap/static/bundles/', // Tell django to use this URL to load packages and not use STATIC_URL + bundle_name
  },

  devtool: 'cheap-module-eval-source-map',

  module: {
    rules: [
      {
        test: /\.css$/,
        loader: 'style-loader!css-loader?sourceMap'
      }, {
        test: /\.scss$/,
        use: [
          {
            loader: "style-loader",
          },
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          }, {
            loader: 'sass-loader',
            options: {
              sourceMap: true
            }
          },
        ]
      }, {
        test: /\.tsx?$/,
        loader: "ts-loader"
      }
    ],
  },

  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(), // don't reload if there is an error
    new webpack.NamedModulesPlugin(),
  ],

}

module.exports = merge.smart(devConfig, commonConfig)

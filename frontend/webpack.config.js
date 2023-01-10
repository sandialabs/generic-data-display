const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry : './src/index.ts',
  mode: 'development',
  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx'],
    modules: [path.resolve('./src'), path.resolve('./node_modules')],
    alias: {
      src: path.join(__dirname, "src")
    }
  },

  plugins: [
    new HtmlWebpackPlugin({
      title: 'Generic Data Display',
    }),
  ],

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        enforce: "pre",
        use: ["source-map-loader"],
      },
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/i,
        use: ['style-loader', 'css-loader'],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
    ],
  },

  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },

  devtool: 'eval-source-map',

  devServer: {
    watchContentBase: true,
    contentBase: path.join(__dirname, 'dist'),
    compress: true,
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8844',
        pathRewrite: {'^/api' : ''}
      },
      '/live': {
        target: 'ws://localhost:8844',
        ws: true,
      },
      '/sidecar': {
        target: 'http://localhost:3000',
        pathRewrite: {'^/sidecar' : ''}
      }
    }
  }
};
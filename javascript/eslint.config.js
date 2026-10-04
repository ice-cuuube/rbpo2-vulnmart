const pluginSecurity = require("eslint-plugin-security");

module.exports = [
    {
        files: ["**/*.js"],

        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "commonjs"
        },

        plugins: {
            security: pluginSecurity
        },

        rules: {
            ...pluginSecurity.configs.recommended.rules
        }
    }
];

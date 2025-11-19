// Physically Based Rendering (PBR) Shader - Unity HLSL
// Implements Disney/Unreal PBR model with Cook-Torrance BRDF

Shader "Custom/PBR Standard"
{
    Properties
    {
        _Color ("Albedo", Color) = (1,1,1,1)
        _MainTex ("Albedo (RGB)", 2D) = "white" {}
        _Metallic ("Metallic", Range(0,1)) = 0.0
        _Smoothness ("Smoothness", Range(0,1)) = 0.5
        _NormalMap ("Normal Map", 2D) = "bump" {}
        _NormalStrength ("Normal Strength", Range(0,2)) = 1.0
        _EmissionColor ("Emission Color", Color) = (0,0,0,1)
        _EmissionMap ("Emission Map", 2D) = "black" {}
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" }
        LOD 200

        Pass
        {
            Name "ForwardBase"
            Tags { "LightMode" = "ForwardBase" }

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fwdbase
            #pragma multi_compile_fog

            #include "UnityCG.cginc"
            #include "Lighting.cginc"
            #include "AutoLight.cginc"

            // Properties
            sampler2D _MainTex;
            float4 _MainTex_ST;
            sampler2D _NormalMap;
            float4 _NormalMap_ST;
            sampler2D _EmissionMap;

            float4 _Color;
            float _Metallic;
            float _Smoothness;
            float _NormalStrength;
            float4 _EmissionColor;

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                float4 tangent : TANGENT;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 worldPos : TEXCOORD1;
                float3 worldNormal : TEXCOORD2;
                float3 worldTangent : TEXCOORD3;
                float3 worldBinormal : TEXCOORD4;
                SHADOW_COORDS(5)
                UNITY_FOG_COORDS(6)
            };

            // ========================================
            // PBR Functions
            // ========================================

            #define PI 3.14159265359

            // Normal Distribution Function (GGX/Trowbridge-Reitz)
            float DistributionGGX(float3 N, float3 H, float roughness)
            {
                float a = roughness * roughness;
                float a2 = a * a;
                float NdotH = max(dot(N, H), 0.0);
                float NdotH2 = NdotH * NdotH;

                float nom = a2;
                float denom = (NdotH2 * (a2 - 1.0) + 1.0);
                denom = PI * denom * denom;

                return nom / denom;
            }

            // Geometry Function (Smith's Schlick-GGX)
            float GeometrySchlickGGX(float NdotV, float roughness)
            {
                float r = (roughness + 1.0);
                float k = (r * r) / 8.0;

                float nom = NdotV;
                float denom = NdotV * (1.0 - k) + k;

                return nom / denom;
            }

            float GeometrySmith(float3 N, float3 V, float3 L, float roughness)
            {
                float NdotV = max(dot(N, V), 0.0);
                float NdotL = max(dot(N, L), 0.0);
                float ggx2 = GeometrySchlickGGX(NdotV, roughness);
                float ggx1 = GeometrySchlickGGX(NdotL, roughness);

                return ggx1 * ggx2;
            }

            // Fresnel (Schlick's approximation)
            float3 FresnelSchlick(float cosTheta, float3 F0)
            {
                return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
            }

            // ========================================
            // Vertex Shader
            // ========================================

            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                o.worldNormal = UnityObjectToWorldNormal(v.normal);
                o.worldTangent = UnityObjectToWorldDir(v.tangent.xyz);
                o.worldBinormal = cross(o.worldNormal, o.worldTangent) * v.tangent.w;

                TRANSFER_SHADOW(o)
                UNITY_TRANSFER_FOG(o, o.pos);

                return o;
            }

            // ========================================
            // Fragment Shader
            // ========================================

            fixed4 frag (v2f i) : SV_Target
            {
                // Sample textures
                float4 albedoSample = tex2D(_MainTex, i.uv) * _Color;
                float3 normalTangent = UnpackNormal(tex2D(_NormalMap, i.uv));
                normalTangent.xy *= _NormalStrength;
                float3 emission = tex2D(_EmissionMap, i.uv).rgb * _EmissionColor.rgb;

                // Transform normal from tangent space to world space
                float3x3 TBN = float3x3(
                    normalize(i.worldTangent),
                    normalize(i.worldBinormal),
                    normalize(i.worldNormal)
                );
                float3 N = normalize(mul(normalTangent, TBN));

                // Calculate vectors
                float3 V = normalize(_WorldSpaceCameraPos - i.worldPos);
                float3 L = normalize(_WorldSpaceLightPos0.xyz);
                float3 H = normalize(V + L);

                // Material properties
                float3 albedo = albedoSample.rgb;
                float metallic = _Metallic;
                float roughness = 1.0 - _Smoothness;

                // Calculate F0 (surface reflection at zero incidence)
                float3 F0 = float3(0.04, 0.04, 0.04); // Dielectric base
                F0 = lerp(F0, albedo, metallic);

                // Cook-Torrance BRDF
                float NDF = DistributionGGX(N, H, roughness);
                float G = GeometrySmith(N, V, L, roughness);
                float3 F = FresnelSchlick(max(dot(H, V), 0.0), F0);

                float3 numerator = NDF * G * F;
                float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
                float3 specular = numerator / denominator;

                // Energy conservation
                float3 kS = F; // Specular contribution
                float3 kD = float3(1.0, 1.0, 1.0) - kS; // Diffuse contribution
                kD *= 1.0 - metallic; // Metals have no diffuse

                float NdotL = max(dot(N, L), 0.0);

                // Combine diffuse and specular
                float3 Lo = (kD * albedo / PI + specular) * _LightColor0.rgb * NdotL;

                // Add ambient (simple)
                float3 ambient = float3(0.03, 0.03, 0.03) * albedo;

                // Shadow attenuation
                float shadow = SHADOW_ATTENUATION(i);

                // Final color
                float3 color = ambient + Lo * shadow + emission;

                // Fog
                UNITY_APPLY_FOG(i.fogCoord, color);

                return float4(color, 1.0);
            }

            ENDCG
        }

        // Shadow casting pass
        Pass
        {
            Tags { "LightMode" = "ShadowCaster" }

            CGPROGRAM
            #pragma vertex vert_shadow
            #pragma fragment frag_shadow
            #include "UnityCG.cginc"

            struct v2f_shadow
            {
                V2F_SHADOW_CASTER;
            };

            v2f_shadow vert_shadow(appdata_base v)
            {
                v2f_shadow o;
                TRANSFER_SHADOW_CASTER_NORMALOFFSET(o)
                return o;
            }

            float4 frag_shadow(v2f_shadow i) : SV_Target
            {
                SHADOW_CASTER_FRAGMENT(i)
            }
            ENDCG
        }
    }

    FallBack "Standard"
}

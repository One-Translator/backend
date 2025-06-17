package com.example.spring_backend.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

  @Value("${build.version:unknown}")
  private String buildVersion;

  @Bean
  public OpenAPI openAPI() {
    return new OpenAPI()
        .components(new Components())
        .info(apiInfo());
  }

  private Info apiInfo() {
    return new Info()
        .title("One-Translator API Documentation") // API의 제목
        .description("피우다 프로젝트 정보통번역기의 API 문서입니다.") // API에 대한 설명
        .version(buildVersion); // 프로젝트의 버전
  }
}

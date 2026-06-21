-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema app_financeiro_v2
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema app_financeiro_v2
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `app_financeiro_v2` DEFAULT CHARACTER SET utf8 ;
USE `app_financeiro_v2` ;

-- -----------------------------------------------------
-- Table `app_financeiro_v2`.`usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `app_financeiro_v2`.`usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome_completo` VARCHAR(150) NOT NULL,
  `nome_usuario` VARCHAR(80) NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `email` VARCHAR(60) NOT NULL,
  `salario_fixo` DECIMAL(10,2) NOT NULL,
  `numero_telefone` VARCHAR(20) NULL,
  `telegram_chat_id` VARCHAR(50) NULL,
  `criado_em` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `ativo` TINYINT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `app_financeiro_v2`.`cartoes_credito`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `app_financeiro_v2`.`cartoes_credito` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(80) NOT NULL,
  `limite` DECIMAL(10,2) NOT NULL,
  `dia_fechamento` INT NOT NULL,
  `dia_vencimento` INT NOT NULL,
  `bandeira` VARCHAR(60) NULL,
  `cor` VARCHAR(7) NULL,
  `id_usuario` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_cartoes_credito_1_idx` (`id_usuario` ASC) VISIBLE,
  CONSTRAINT `fk_cartoes_credito_1`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `app_financeiro_v2`.`usuarios` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `app_financeiro_v2`.`despesas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `app_financeiro_v2`.`despesas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `local` VARCHAR(80) NOT NULL,
  `valor_total` DECIMAL(10,2) NOT NULL,
  `parcelas` INT NOT NULL,
  `descricao` VARCHAR(150) NULL,
  `categoria` VARCHAR(60) NOT NULL,
  `data_compra` DATE NOT NULL,
  `data_primeiro_pagamento` DATE NULL,
  `dia_vencimento` INT NULL,
  `id_usuario` INT NOT NULL,
  `id_cartao` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_despesas_1_idx` (`id_usuario` ASC) VISIBLE,
  INDEX `fk_despesas_2_idx` (`id_cartao` ASC) VISIBLE,
  CONSTRAINT `fk_despesas_1`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `app_financeiro_v2`.`usuarios` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_despesas_2`
    FOREIGN KEY (`id_cartao`)
    REFERENCES `app_financeiro_v2`.`cartoes_credito` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `app_financeiro_v2`.`receitas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `app_financeiro_v2`.`receitas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fonte` VARCHAR(60) NOT NULL,
  `valor` DECIMAL(10,2) NOT NULL,
  `descricao` VARCHAR(100) NULL,
  `data_recebimento` DATE NOT NULL,
  `id_usuario` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_receitas_1_idx` (`id_usuario` ASC) VISIBLE,
  CONSTRAINT `fk_receitas_1`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `app_financeiro_v2`.`usuarios` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `app_financeiro_v2`.`assinaturas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `app_financeiro_v2`.`assinaturas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `valor` DECIMAL(10,2) NOT NULL,
  `descricao` VARCHAR(150) NULL,
  `categoria` VARCHAR(60) NOT NULL,
  `data_aquisicao` DATE NOT NULL,
  `data_primeiro_pagamento` DATE NULL,
  `dia_vencimento` INT NULL,
  `id_usuario` INT NOT NULL,
  `id_cartao` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_assinaturas_1_idx` (`id_usuario` ASC) VISIBLE,
  INDEX `fk_assinaturas_2_idx` (`id_cartao` ASC) VISIBLE,
  CONSTRAINT `fk_assinaturas_1`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `app_financeiro_v2`.`usuarios` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assinaturas_2`
    FOREIGN KEY (`id_cartao`)
    REFERENCES `app_financeiro_v2`.`cartoes_credito` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

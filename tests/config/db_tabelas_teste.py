


#BIBLIO VIA PIP
import MySQLdb

def inicializar_banco_completo(conn: MySQLdb.Connection):
    """Garante a criação de todas as tabelas na ordem correta de dependência."""
    cursor = conn.cursor()
    
    # usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `usuarios` (
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
            PRIMARY KEY (`id`)
        )
    """)

    # Cartoes_creditos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `cartoes_credito` (
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
          REFERENCES `usuarios` (`id`)
          ON DELETE NO ACTION
          ON UPDATE NO ACTION)
    """)

    #Despesas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `despesas` (
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
          REFERENCES `usuarios` (`id`)
          ON DELETE NO ACTION
          ON UPDATE NO ACTION,
        CONSTRAINT `fk_despesas_2`
          FOREIGN KEY (`id_cartao`)
          REFERENCES `cartoes_credito` (`id`)
          ON DELETE NO ACTION
          ON UPDATE NO ACTION)
                   
    """)

    #Receitas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `receitas` (
        id` INT NOT NULL AUTO_INCREMENT,
        `fonte` VARCHAR(60) NOT NULL,
        `valor` DECIMAL(10,2) NOT NULL,
        `descricao` VARCHAR(100) NULL,
        `data_recebimento` DATE NOT NULL,
        `id_usuario` INT NOT NULL,
        PRIMARY KEY (`id`),
        INDEX `fk_receitas_1_idx` (`id_usuario` ASC) VISIBLE,
        CONSTRAINT `fk_receitas_1`
          FOREIGN KEY (`id_usuario`)
          REFERENCES `usuarios` (`id`)
          ON DELETE NO ACTION
          ON UPDATE NO ACTION)
    """)
    
    #assinaturas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `assinaturas` (
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
          REFERENCES `usuarios` (`id`)
          ON DELETE NO ACTION
          ON UPDATE NO ACTION,
        CONSTRAINT `fk_assinaturas_2`
          FOREIGN KEY (`id_cartao`)
          REFERENCES `cartoes_credito` (`id`)
          ON DELETE NO ACTION
          ON UPDATE NO ACTION)
    """)

    conn.commit()
    cursor.close()
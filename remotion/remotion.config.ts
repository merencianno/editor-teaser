import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// Máquina carregada faz o OffthreadVideo repetir quadros (a imagem "engasga"). Os scripts passam --concurrency
// conforme a máquina; este é só o padrão do Studio.
Config.setConcurrency(4);
